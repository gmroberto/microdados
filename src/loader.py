"""
Data loader for ENEM Microdata Pipeline.

This module handles loading CSV data into PostgreSQL database tables.
"""

import logging
import pandas as pd
from pathlib import Path
from typing import List, Optional
from database import DatabaseManager
from config import get_path, get_setting

# Set up logging
logger = logging.getLogger(__name__)

class ENEMLoader:
    """
    Handles loading ENEM microdata CSV files into PostgreSQL database.
    
    This class provides functionality to:
    - Load CSV files into database tables
    - Create united tables
    - Create database indexes
    - Handle large datasets with chunked processing
    """
    
    def __init__(self):
        """Initialize the ENEMLoader with database connection."""
        self.db_manager = DatabaseManager()
        self.chunk_size = get_setting('chunk_size', 10000)
    
    def load_all_files(self, folder_path: str) -> bool:
        """
        Load all CSV files from the specified folder.
        
        Args:
            folder_path: Path to folder containing CSV files
            
        Returns:
            True if all files were loaded successfully, False otherwise
        """
        try:
            folder = Path(folder_path)
            if not folder.exists():
                logger.error(f"Folder does not exist: {folder_path}")
                return False
            
            # Find all CSV files
            csv_files = list(folder.glob("*.csv"))
            if not csv_files:
                logger.warning("No CSV files found to load")
                return True
            
            logger.info(f"Found {len(csv_files)} CSV files to load")
            
            # Load each file
            success_count = 0
            for csv_file in csv_files:
                try:
                    if self.load_file(csv_file):
                        success_count += 1
                except Exception as e:
                    logger.error(f"Error loading {csv_file}: {e}")
            
            if success_count == len(csv_files):
                logger.info("All files loaded successfully")
                return True
            else:
                logger.warning(f"Loaded {success_count}/{len(csv_files)} files successfully")
                return False
                
        except Exception as e:
            logger.error(f"Error in load_all_files: {e}")
            return False
    
    def load_file(self, file_path: Path) -> bool:
        """
        Load a single CSV file into the database.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            True if file was loaded successfully, False otherwise
        """
        try:
            # Extract table name from filename
            table_name = self._get_table_name_from_file(file_path)
            
            # Read CSV file
            logger.info(f"Loading {file_path} into table {table_name}")
            
            # Load data in chunks to handle large files
            chunk_count = 0
            for chunk in pd.read_csv(file_path, chunksize=self.chunk_size, low_memory=False):
                chunk_count += 1
                logger.debug(f"Processing chunk {chunk_count} of {file_path}")
                
                # Create table if it doesn't exist (only for first chunk)
                if chunk_count == 1:
                    self._create_table_if_not_exists(table_name, chunk)
                
                # Insert chunk data
                self._insert_chunk(table_name, chunk)
            
            logger.info(f"Successfully loaded {file_path} ({chunk_count} chunks)")
            return True
            
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            return False
    
    def _get_table_name_from_file(self, file_path: Path) -> str:
        """Extract table name from CSV filename."""
        # Remove extension and convert to lowercase
        table_name = file_path.stem.lower()
        
        # Replace spaces and special characters with underscores
        table_name = table_name.replace(' ', '_').replace('-', '_')
        
        return table_name
    
    def _create_table_if_not_exists(self, table_name: str, df: pd.DataFrame) -> None:
        """Create table if it doesn't exist."""
        try:
            # Check if table exists
            check_query = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """
            result = self.db_manager.execute_query(check_query, (table_name,))
            table_exists = result[0][0] if result else False
            
            if table_exists:
                logger.debug(f"Table {table_name} already exists")
                return
            
            # Create table based on DataFrame structure
            columns = []
            for col_name, dtype in df.dtypes.items():
                # Map pandas dtypes to PostgreSQL types
                pg_type = self._map_pandas_to_postgresql_type(dtype)
                columns.append(f"{col_name} {pg_type}")
            
            create_sql = f"""
                CREATE TABLE {table_name} (
                    {', '.join(columns)}
                )
            """
            
            self.db_manager.execute_query(create_sql)
            logger.info(f"Created table {table_name}")
            
        except Exception as e:
            logger.error(f"Error creating table {table_name}: {e}")
            raise
    
    def _map_pandas_to_postgresql_type(self, dtype) -> str:
        """Map pandas data types to PostgreSQL types."""
        if pd.api.types.is_integer_dtype(dtype):
            return 'INTEGER'
        elif pd.api.types.is_float_dtype(dtype):
            return 'DOUBLE PRECISION'
        elif pd.api.types.is_bool_dtype(dtype):
            return 'BOOLEAN'
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return 'TIMESTAMP'
        else:
            return 'TEXT'
    
    def _insert_chunk(self, table_name: str, chunk: pd.DataFrame) -> None:
        """Insert a chunk of data into the table."""
        try:
            # Convert DataFrame to list of tuples for insertion
            data = [tuple(row) for row in chunk.values]
            
            if not data:
                return
            
            # Build INSERT query
            columns = list(chunk.columns)
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join(columns)
            
            insert_sql = f"""
                INSERT INTO {table_name} ({columns_str})
                VALUES ({placeholders})
            """
            
            # Execute batch insert
            self.db_manager.execute_batch(insert_sql, data)
            
        except Exception as e:
            logger.error(f"Error inserting chunk into {table_name}: {e}")
            raise
    
    def create_united_table(self, table_name: str = None, drop_if_exists: bool = False) -> bool:
        """
        Create the united table.
        
        Args:
            table_name: Name of the united table
            drop_if_exists: If True, drop the table if it already exists
            
        Returns:
            True if table was created successfully, False otherwise
        """
        try:
            from united_table_logic import UnitedTableLogic
            
            table_name = table_name or get_setting('united_table_name', 'enem_microdado_2011_2023')
            logger.info(f"Creating united table: {table_name}")
            
            logic = UnitedTableLogic(table_name)
            success = logic.create_united_table(drop_if_exists=drop_if_exists)
            logic.close()
            
            if success:
                logger.info(f"Successfully created united table: {table_name}")
            else:
                logger.warning(f"United table {table_name} already exists or creation failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error creating united table: {e}")
            return False
    
    def populate_united_table(self, table_name: str = None) -> bool:
        """
        Populate the united table with data from year-specific tables.
        
        Args:
            table_name: Name of the united table
            
        Returns:
            True if population was successful, False otherwise
        """
        try:
            from united_table_logic import UnitedTableLogic
            
            table_name = table_name or get_setting('united_table_name', 'enem_microdado_2011_2023')
            logger.info(f"Populating united table: {table_name}")
            
            logic = UnitedTableLogic(table_name)
            success = logic.populate_united_table()
            logic.close()
            
            if success:
                logger.info(f"Successfully populated united table: {table_name}")
            else:
                logger.warning(f"Failed to populate united table: {table_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error populating united table: {e}")
            return False
    
    def create_indexes(self, table_name: str = None) -> bool:
        """
        Create indexes for the specified table.
        
        Args:
            table_name: Name of the table to create indexes for
            
        Returns:
            True if indexes were created successfully, False otherwise
        """
        try:
            from united_table_logic import UnitedTableLogic
            
            table_name = table_name or get_setting('united_table_name', 'enem_microdado_2011_2023')
            logger.info(f"Creating indexes for: {table_name}")
            
            logic = UnitedTableLogic(table_name)
            success = logic.create_united_table_indexes()
            logic.close()
            
            return success
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            return False
    
    def get_united_table_info(self) -> dict:
        """Get information about the united table."""
        try:
            from united_table_logic import UnitedTableLogic
            
            table_name = get_setting('united_table_name', 'enem_microdado_2011_2023')
            logic = UnitedTableLogic(table_name)
            info = logic.get_united_table_info()
            logic.close()
            return info
        except Exception as e:
            logger.error(f"Error getting united table info: {e}")
            return {}
    
    def close(self):
        """Close database connections."""
        if self.db_manager:
            self.db_manager.close() 