import logging
import psycopg2
from typing import Dict, Any, Optional
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from io import StringIO
import yaml

from config import config_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Centralized database operations for the ENEM microdata project."""
    
    def __init__(self, database_type: str = "etl"):
        """
        Initialize DatabaseManager.
        
        Args:
            database_type: Either "etl" for the ETL database or "airflow" for the Airflow database
        """
        self.database_type = database_type
        
        # Get database configuration using the new config manager
        config = config_manager.get_database_config(database_type)
        
        if not config:
            raise ValueError(f"No configuration found for database type: {database_type}")
        
        # Validate required configuration
        required_keys = ['user', 'password', 'host', 'port', 'database']
        missing_keys = [key for key in required_keys if not config.get(key)]
        if missing_keys:
            raise ValueError(f"Missing required database configuration: {missing_keys}")
        
        # URL encode the password to handle special characters
        from urllib.parse import quote_plus
        encoded_password = quote_plus(config['password'])
        
        self.connection_string = (
            f"postgresql://{config['user']}:{encoded_password}@"
            f"{config['host']}:{config['port']}/{config['database']}"
        )
        
        # Log connection attempt (without password)
        safe_connection_string = (
            f"postgresql://{config['user']}:***@{config['host']}:{config['port']}/{config['database']}"
        )
        logger.info(f"Attempting to connect to database: {safe_connection_string}")
        
        try:
            # Create engine with proper PostgreSQL configuration for Portuguese text
            self.engine = create_engine(
                self.connection_string,
                connect_args={
                    'client_encoding': 'latin1',  # Use Latin encoding for Portuguese
                    'options': '-c client_encoding=latin1'
                },
                # Add additional parameters for connection management
                pool_pre_ping=True,
                pool_recycle=300
            )
            # Test the connection with explicit encoding handling
            with self.engine.connect() as conn:
                # Set encoding explicitly on the connection for Portuguese text
                conn.execute(text("SET client_encoding TO 'LATIN1'"))
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established successfully with Latin encoding")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            logger.error(f"Connection string (without password): {safe_connection_string}")
            logger.error(f"Error type: {type(e).__name__}")
            raise ConnectionError(f"Database connection failed: {e}")
    
    @classmethod
    def create_etl_manager(cls):
        """Create a DatabaseManager instance for the ETL database."""
        return cls("etl")
    
    @classmethod
    def create_airflow_manager(cls):
        """Create a DatabaseManager instance for the Airflow database."""
        return cls("airflow")
    
    def load_schema(self, table_name: str) -> Dict:
        """Load table schema from YAML file."""
        schema_path = config_manager.get_schema_path()
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schemas = yaml.safe_load(f)
            return schemas.get(table_name, {})
        except Exception as e:
            print(f"Error loading schema for {table_name}: {e}")
            return {}
    
    def get_schema_dtypes(self, table_name: str) -> Dict[str, str]:
        """Get pandas dtypes from schema."""
        schema = self.load_schema(table_name)
        columns = schema.get('columns', {})
        
        type_mapping = {
            'INTEGER': 'Int64',
            'BIGINT': 'Int64',
            'DECIMAL': 'float64',
            'FLOAT': 'float64',
            'TEXT': 'object',
            'DATE': 'datetime64[ns]',
            'BOOLEAN': 'boolean'
        }
        
        return {col: type_mapping.get(dtype, 'object') for col, dtype in columns.items()}
    
    def create_table(self, table_name: str, df: pd.DataFrame, drop_if_exists: bool = False) -> bool:
        """Create table with proper schema. Returns True if table was created, False if it already exists."""
        try:
            # Check if table already exists
            if self.table_exists(table_name):
                logger.info(f"Table {table_name} already exists, skipping creation")
                return False
            
            schema = self.load_schema(table_name)
            columns = schema.get('columns', {})
            
            logger.debug(f"Loaded schema for {table_name}: {schema}")
            logger.debug(f"Schema columns count: {len(columns)}")
            
            if not columns:
                logger.warning(f"No schema found for {table_name}, using DataFrame columns")
                columns = {col: 'TEXT' for col in df.columns}
            
            # Clean column names
            df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
            
            # Create column definitions
            column_defs = []
            logger.debug(f"Schema columns: {list(columns.keys())}")
            logger.debug(f"DataFrame columns: {list(df.columns)}")
            
            # Check for column name mismatches
            missing_in_schema = [col for col in df.columns if col not in columns]
            if missing_in_schema:
                logger.warning(f"Columns not found in schema: {missing_in_schema}")
            
            for col in df.columns:
                col_type = columns.get(col, 'TEXT')
                # Ensure we always have a valid data type
                if not col_type or col_type.strip() == '':
                    col_type = 'TEXT'
                    logger.warning(f"Column {col} not found in schema, using TEXT")
                logger.debug(f"Column {col}: type {col_type}")
                column_defs.append(f"{col} {col_type}")
            
            logger.info(f"Creating table {table_name} with {len(column_defs)} columns")
            
            with self.engine.begin() as conn:
                if drop_if_exists:
                    logger.info(f"Dropping existing table {table_name} if it exists")
                    conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
                
                create_sql = f"CREATE TABLE {table_name} ({', '.join(column_defs)})"
                logger.debug(f"Executing SQL: {create_sql}")
                conn.execute(text(create_sql))
                logger.info(f"Successfully created table {table_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating table {table_name}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            raise
    
    def insert_data(self, table_name: str, df: pd.DataFrame) -> None:
        """Insert DataFrame into table using PostgreSQL COPY."""
        try:
            logger.debug(f"Inserting data into {table_name}")
            logger.debug(f"DataFrame shape: {df.shape}")
            logger.debug(f"DataFrame columns: {list(df.columns)}")
            
            buffer = StringIO()
            df.to_csv(buffer, index=False, header=False, sep='\t', na_rep='\\N')
            buffer.seek(0)
            
            with self.engine.connect() as conn:
                raw_conn = conn.connection.driver_connection
                with raw_conn.cursor() as cursor:
                    cursor.copy_from(
                        buffer,
                        table_name,
                        sep='\t',
                        null='\\N',
                        columns=df.columns.tolist()
                    )
                raw_conn.commit()
                
            logger.debug(f"Successfully inserted {len(df)} rows into {table_name}")
            
        except Exception as e:
            logger.error(f"Error inserting data into {table_name}: {e}")
            logger.error(f"DataFrame shape: {df.shape}")
            logger.error(f"DataFrame columns: {list(df.columns)}")
            
            # Log sample data for debugging
            if not df.empty:
                logger.error(f"Sample data (first row): {df.iloc[0].to_dict()}")
            
            raise
    

    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """Execute a SQL query and return results."""
        try:
            logger.debug(f"Executing query: {query}")
            with self.engine.connect() as conn:
                if params:
                    # Convert %s placeholders to :param style for SQLAlchemy
                    formatted_query = query
                    for i, param in enumerate(params):
                        formatted_query = formatted_query.replace('%s', f':param_{i}', 1)
                    param_dict = {f'param_{i}': param for i, param in enumerate(params)}
                    result = conn.execute(text(formatted_query), param_dict)
                else:
                    result = conn.execute(text(query))
                
                # Fetch all results if it's a SELECT query
                if query.strip().upper().startswith('SELECT'):
                    rows = result.fetchall()
                    logger.debug(f"Query returned {len(rows)} rows")
                    return rows
                else:
                    logger.debug("Query executed successfully")
                    return []
                    
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    def execute_batch_simple(self, query: str, data: list) -> None:
        """Execute batch insert/update operations using direct psycopg2."""
        try:
            logger.debug(f"Executing batch query: {query}")
            logger.debug(f"Data size: {len(data)}")
            
            with self.engine.connect() as conn:
                raw_conn = conn.connection.driver_connection
                with raw_conn.cursor() as cursor:
                    # Set encoding explicitly for Portuguese text
                    cursor.execute("SET client_encoding TO 'LATIN1'")
                    
                    # Execute batch insert
                    cursor.executemany(query, data)
                    
                raw_conn.commit()
            
            logger.debug("Batch query executed successfully")
        except Exception as e:
            logger.error(f"Error executing batch query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Data size: {len(data)}")
            
            # Log sample data for debugging
            if data and len(data) > 0:
                logger.error(f"Sample data row: {data[0]}")
                logger.error(f"Sample data types: {[type(val) for val in data[0]]}")
            
            raise


    
    def create_indexes(self, table_name: str) -> None:
        """Create indexes for the table."""
        schema = self.load_schema(table_name)
        indexes = schema.get('indexes', [])
        
        with self.engine.begin() as conn:
            for i, index in enumerate(indexes):
                columns = index.get('index_columns', [])
                if not columns:
                    logger.warning(f"No index_columns found in index config {i} for table {table_name}")
                    continue
                
                # Generate index name
                index_name = f"idx_{table_name}_{'_'.join(columns)}"
                
                # Check if index already exists
                check_query = "SELECT EXISTS (SELECT FROM pg_indexes WHERE indexname = :index_name)"
                result = conn.execute(text(check_query), {"index_name": index_name})
                index_exists = result.scalar()
                
                if index_exists:
                    logger.info(f"Index {index_name} already exists, skipping")
                    continue
                
                # Create index
                columns_str = ', '.join(columns)
                create_index_sql = f"CREATE INDEX {index_name} ON {table_name} ({columns_str})"
                conn.execute(text(create_index_sql))
                logger.info(f"Created index {index_name} on columns: {columns_str}")
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table_name)"
                ), {"table_name": table_name})
                exists = result.scalar()
                logger.debug(f"Table {table_name} exists: {exists}")
                return exists
        except Exception as e:
            logger.error(f"Error checking if table {table_name} exists: {e}")
            return False
    
    def table_has_data(self, table_name: str) -> bool:
        """Check if a table has any data (rows)."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                logger.debug(f"Table {table_name} has {count} rows")
                return count > 0
        except Exception as e:
            logger.error(f"Error checking if table {table_name} has data: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test database connection and return True if successful."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        self.engine.dispose() 