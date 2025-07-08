"""
United Table Logic for ENEM Microdata Pipeline.

This module handles the creation and management of a unified table that combines
ENEM microdata from multiple years into a single optimized table.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from database import DatabaseManager

# Set up logging
logger = logging.getLogger(__name__)

class UnitedTableLogic:
    """
    Handles the creation and management of a unified ENEM microdata table.
    
    This class provides functionality to:
    - Create a unified table schema
    - Populate the table with data from multiple years
    - Create optimized indexes for performance
    """
    
    def __init__(self, table_name: str = None):
        """
        Initialize the UnitedTableLogic.
        
        Args:
            table_name: Name of the united table (defaults to config setting)
        """
        from config import get_setting
        
        self.table_name = table_name or get_setting('united_table_name', 'enem_microdado_2011_2023')
        self.db_manager = DatabaseManager()
        self.schemas = self._load_schemas()
    
    def _load_schemas(self) -> Dict[str, Any]:
        """Load table schemas from configuration."""
        try:
            from config import get_schema_path
            schema_path = get_schema_path()
            
            if not schema_path.exists():
                logger.warning(f"Schema file not found: {schema_path}")
                return {}
            
            with open(schema_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Error loading schemas: {e}")
            return {}
    
    def get_united_table_info(self) -> Dict[str, Any]:
        """Get information about the united table."""
        united_schema = self.schemas.get(self.table_name, {})
        columns = united_schema.get('columns', {})
        indexes = united_schema.get('indexes', [])
        
        return {
            'table_name': self.table_name,
            'column_count': len(columns),
            'index_count': len(indexes),
            'columns': list(columns.keys()),
            'indexes': [idx.get('name', '') for idx in indexes]
        }
    
    def _get_year_tables(self) -> List[str]:
        """Get list of year-specific tables that exist in the database."""
        try:
            query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'enem_microdado_%'
                AND table_name != %s
                ORDER BY table_name
            """
            result = self.db_manager.execute_query(query, (self.table_name,))
            return [row[0] for row in result] if result else []
        except Exception as e:
            logger.error(f"Error getting year tables: {e}")
            return []
    
    def _get_common_columns(self, table1: str, table2: str) -> List[str]:
        """Get common columns between two tables."""
        try:
            query = """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s
                INTERSECT
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s
                ORDER BY column_name
            """
            result = self.db_manager.execute_query(query, (table1, table2))
            return [row[0] for row in result] if result else []
        except Exception as e:
            logger.error(f"Error getting common columns: {e}")
            return []
    
    def _generate_insert_queries(self) -> List[str]:
        """Generate INSERT queries for populating the united table."""
        queries = []
        year_tables = self._get_year_tables()
        
        for year_table in year_tables:
            if year_table not in self.schemas:
                logger.warning(f"No schema found for {year_table}")
                continue
            
            common_columns = self._get_common_columns(self.table_name, year_table)
            if not common_columns:
                logger.warning(f"No common columns between {self.table_name} and {year_table}")
                continue
            
            columns_str = ', '.join(common_columns)
            query = f"""
                INSERT INTO {self.table_name} ({columns_str})
                SELECT {columns_str}
                FROM {year_table}
            """
            queries.append(query)
        
        return queries
    
    def create_united_table(self, drop_if_exists: bool = False) -> bool:
        """
        Create the united table.
        
        Args:
            drop_if_exists: If True, drop the table if it already exists
            
        Returns:
            True if table was created successfully, False otherwise
        """
        try:
            # Check if table already exists
            check_query = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """
            result = self.db_manager.execute_query(check_query, (self.table_name,))
            table_exists = result[0][0] if result else False
            
            if table_exists:
                if drop_if_exists:
                    logger.info(f"Dropping existing table: {self.table_name}")
                    self.db_manager.execute_query(f"DROP TABLE {self.table_name}")
                else:
                    logger.info(f"Table {self.table_name} already exists, skipping creation")
                    return True
            
            # Get schema for united table
            united_schema = self.schemas.get(self.table_name)
            if not united_schema:
                logger.error(f"No schema found for {self.table_name}")
                return False
            
            # Create table
            logger.info(f"Creating united table: {self.table_name}")
            create_sql = self._generate_create_table_sql(united_schema)
            self.db_manager.execute_query(create_sql)
            
            logger.info(f"Successfully created united table: {self.table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating united table: {e}")
            return False
    
    def _generate_create_table_sql(self, schema: Dict[str, Any]) -> str:
        """Generate CREATE TABLE SQL from schema."""
        columns = schema.get('columns', {})
        column_definitions = []
        
        for col_name, col_type in columns.items():
            column_definitions.append(f"{col_name} {col_type}")
        
        columns_sql = ', '.join(column_definitions)
        return f"CREATE TABLE {self.table_name} ({columns_sql})"
    
    def populate_united_table(self) -> bool:
        """
        Populate the united table with data from year-specific tables.
        
        Returns:
            True if population was successful, False otherwise
        """
        try:
            logger.info(f"Populating united table: {self.table_name}")
            
            # Check if table already has data
            count_query = f"SELECT COUNT(*) FROM {self.table_name}"
            result = self.db_manager.execute_query(count_query)
            row_count = result[0][0] if result else 0
            
            if row_count > 0:
                logger.info(f"Table {self.table_name} already has data, skipping population")
                return True
            
            logger.info(f"Table {self.table_name} is empty, proceeding with population")
            
            # Generate and execute insert queries
            queries = self._generate_insert_queries()
            if not queries:
                logger.warning("No queries generated for populating united table")
                return False
            
            logger.info(f"Found {len(queries)} year tables to process")
            
            for query in queries:
                # Extract table name from query for logging
                year_table = query.split('FROM ')[-1].split()[0]
                logger.info(f"Inserting data from {year_table}...")
                
                try:
                    self.db_manager.execute_query(query)
                    logger.info(f"Successfully inserted data from {year_table}")
                except Exception as e:
                    logger.error(f"Error inserting data from {year_table}: {e}")
                    # Continue with other tables even if one fails
            
            logger.info(f"Successfully populated united table: {self.table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error populating united table: {e}")
            return False
    
    def create_united_table_indexes(self) -> bool:
        """
        Create indexes for the united table.
        
        Returns:
            True if indexes were created successfully, False otherwise
        """
        try:
            logger.info(f"Creating indexes for united table: {self.table_name}")
            
            united_schema = self.schemas.get(self.table_name)
            if not united_schema:
                logger.error(f"No schema found for {self.table_name}")
                return False
            
            indexes = united_schema.get('indexes', [])
            if not indexes:
                logger.warning(f"No indexes defined in schema for {self.table_name}")
                return True
            
            for index_config in indexes:
                index_name = index_config.get('name')
                index_columns = index_config.get('columns', [])
                
                if not index_name or not index_columns:
                    continue
                
                # Check if index already exists
                check_query = """
                    SELECT EXISTS (
                        SELECT FROM pg_indexes 
                        WHERE indexname = %s
                    )
                """
                result = self.db_manager.execute_query(check_query, (index_name,))
                index_exists = result[0][0] if result else False
                
                if index_exists:
                    logger.info(f"Index {index_name} already exists, skipping")
                    continue
                
                # Create index
                columns_str = ', '.join(index_columns)
                create_index_sql = f"CREATE INDEX {index_name} ON {self.table_name} ({columns_str})"
                self.db_manager.execute_query(create_index_sql)
                logger.info(f"Created index {index_name}")
            
            logger.info(f"Successfully created indexes for united table: {self.table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            return False
    
    def close(self):
        """Close database connections."""
        if self.db_manager:
            self.db_manager.close() 