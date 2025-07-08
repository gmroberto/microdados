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
            # Create engine with proper PostgreSQL configuration
            self.engine = create_engine(
                self.connection_string,
                connect_args={
                    'client_encoding': 'utf8',
                    'options': '-c client_encoding=utf8'
                },
                # Add additional parameters for connection management
                pool_pre_ping=True,
                pool_recycle=300
            )
            # Test the connection with explicit encoding handling
            with self.engine.connect() as conn:
                # Set encoding explicitly on the connection
                conn.execute(text("SET client_encoding TO 'UTF8'"))
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established successfully")
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
            with open(schema_path, 'r') as f:
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
        schema = self.load_schema(table_name)
        columns = schema.get('columns', {})
        
        # Prepare DataFrame for insertion
        df_prepared = self._prepare_dataframe(df, columns)
        
        buffer = StringIO()
        df_prepared.to_csv(buffer, index=False, header=False, sep='\t', na_rep='\\N')
        buffer.seek(0)
        
        with self.engine.connect() as conn:
            raw_conn = conn.connection.driver_connection
            with raw_conn.cursor() as cursor:
                cursor.copy_from(
                    buffer,
                    table_name,
                    sep='\t',
                    null='\\N',
                    columns=df_prepared.columns.tolist()
                )
            raw_conn.commit()
    
    def _prepare_dataframe(self, df: pd.DataFrame, schema: Dict[str, str]) -> pd.DataFrame:
        """Prepare DataFrame for database insertion."""
        df_copy = df.copy()
        
        for column, pg_type in schema.items():
            if column not in df_copy.columns:
                continue
                
            pg_type = pg_type.upper()
            if pg_type == 'BOOLEAN':
                df_copy[column] = df_copy[column].map({'1': 'true', '0': 'false'})
            elif pg_type in ('INTEGER', 'BIGINT'):
                df_copy[column] = pd.to_numeric(df_copy[column], errors='coerce')
                mask = df_copy[column].notna()
                df_copy.loc[mask, column] = df_copy.loc[mask, column].apply(
                    lambda x: str(int(x)) if not pd.isna(x) else '\\N'
                )
                df_copy[column] = df_copy[column].fillna('\\N')
            elif pg_type in ('DOUBLE PRECISION', 'DECIMAL', 'FLOAT'):
                df_copy[column] = pd.to_numeric(df_copy[column], errors='coerce')
                df_copy[column] = df_copy[column].astype(str).replace({'nan': '\\N'})
                df_copy[column] = df_copy[column].apply(
                    lambda x: x.replace(',', '.') if x != '\\N' else x
                )
        
        return df_copy.replace({'nan': '\\N', 'None': '\\N'})
    
    def execute_query(self, query: str) -> None:
        """Execute a SQL query."""
        try:
            logger.debug(f"Executing query: {query}")
            with self.engine.begin() as conn:
                conn.execute(text(query))
            logger.debug("Query executed successfully")
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            raise
    
    def create_indexes(self, table_name: str) -> None:
        """Create indexes for the table."""
        schema = self.load_schema(table_name)
        indexes = schema.get('indexes', [])
        
        with self.engine.begin() as conn:
            for index in indexes:
                columns = index.get('index_columns', [])
                for column in columns:
                    index_name = f"idx_{table_name}_{column}"
                    create_index_sql = f"CREATE INDEX {index_name} ON {table_name} ({column})"
                    conn.execute(text(create_index_sql))
    
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