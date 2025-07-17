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

def _detect_and_read_csv(file_path: Path, chunk_size: int = 10000):
    """
    Read CSV file with automatic encoding and delimiter detection.
    Tries multiple encodings and delimiters to handle different file formats.
    Default encoding is Latin for Portuguese text.
    """
    # Start with Latin encodings for Portuguese text
    encodings = ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8', 'utf-8-sig']
    delimiters = [';', ',']  # ENEM files typically use semicolons
    
    for encoding in encodings:
        for delimiter in delimiters:
            try:
                # Try reading just the header to check column count
                df = pd.read_csv(file_path, encoding=encoding, sep=delimiter, nrows=1)
                if len(df.columns) > 1:
                    # If more than one column, use this delimiter
                    logger.debug(f"Detected encoding={encoding}, delimiter='{delimiter}' for {file_path}")
                    for chunk in pd.read_csv(
                        file_path, 
                        chunksize=chunk_size, 
                        low_memory=False, 
                        encoding=encoding, 
                        sep=delimiter,
                        na_values=['', 'nan', 'NaN', 'NULL', 'null'],
                        keep_default_na=False
                    ):
                        yield chunk
                    return
            except Exception as e:
                logger.debug(f"Failed with encoding={encoding}, delimiter='{delimiter}': {e}")
                continue
    
    # Fallback: try with error handling and semicolon
    logger.warning(f"All encoding/delimiter combinations failed for {file_path}, trying fallback with error handling")
    try:
        for chunk in pd.read_csv(
            file_path, 
            chunksize=chunk_size, 
            low_memory=False, 
            encoding='latin-1', 
            errors='replace', 
            sep=';',
            na_values=['', 'nan', 'NaN', 'NULL', 'null'],
            keep_default_na=False
        ):
            yield chunk
        logger.warning(f"Successfully read {file_path} with fallback error handling")
    except Exception as e:
        logger.error(f"Failed to read {file_path} even with fallback error handling: {e}")
        raise

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
            skipped_count = 0
            failed_count = 0
            
            for csv_file in csv_files:
                try:
                    # Check if we should skip this file before processing
                    table_name = self._get_table_name_from_file(csv_file)
                    if self._should_skip_table_load(table_name):
                        logger.info(f"Skipping {csv_file} - table {table_name} already exists with data")
                        skipped_count += 1
                        continue
                    
                    if self.load_file(csv_file):
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Error loading {csv_file}: {e}")
                    failed_count += 1
            
            # Log summary
            logger.info(f"Load summary: {success_count} files loaded, {skipped_count} files skipped (existing tables), {failed_count} files failed")
            
            if failed_count == 0:
                logger.info("All files processed successfully")
                return True
            else:
                logger.warning(f"Some files failed to load: {failed_count} failures out of {len(csv_files)} total files")
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
            
            # Check if table already exists and has data - early performance optimization
            if self._should_skip_table_load(table_name):
                logger.info(f"Table {table_name} already exists and has data, skipping load for {file_path}")
                return True
            
            # Read CSV file
            logger.info(f"Loading {file_path} into table {table_name}")
            
            # Load data in chunks to handle large files with automatic encoding detection
            chunk_count = 0
            for chunk in _detect_and_read_csv(file_path, self.chunk_size):
                chunk_count += 1
                logger.debug(f"Processing chunk {chunk_count} of {file_path}")
                
                # Create table if it doesn't exist (only for first chunk)
                if chunk_count == 1:
                    try:
                        self.db_manager.create_table(table_name, chunk, drop_if_exists=False)
                    except Exception as e:
                        logger.error(f"Error creating table {table_name}: {e}")
                        raise
                
                # Prepare and insert chunk data
                if not chunk.empty:
                    try:
                        # Clean column names to match schema
                        chunk.columns = [col.strip().lower().replace(' ', '_') for col in chunk.columns]
                        
                        # Prepare the data for database insertion
                        prepared_chunk = self._prepare_dataframe(chunk, table_name)
                        
                        # Use the database manager's insert_data method
                        self.db_manager.insert_data(table_name, prepared_chunk)
                        
                        logger.debug(f"Successfully inserted chunk with {len(chunk)} rows into {table_name}")
                    except Exception as e:
                        logger.error(f"Error inserting chunk into {table_name}: {e}")
                        logger.error(f"Chunk shape: {chunk.shape}")
                        logger.error(f"Chunk columns: {list(chunk.columns)}")
                        raise
                else:
                    logger.warning(f"No data to insert for chunk in {table_name}")
            
            logger.info(f"Successfully loaded {file_path} ({chunk_count} chunks)")
            return True
            
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            return False
    
    def _should_skip_table_load(self, table_name: str) -> bool:
        """
        Check if we should skip loading a table based on its current state.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if the table exists and has data, False otherwise
        """
        try:
            # Check if skipping existing tables is enabled
            skip_existing = get_setting('skip_existing_tables', True)
            if not skip_existing:
                logger.debug(f"Skipping existing tables is disabled, will process {table_name}")
                return False
            
            # Check if table exists
            if not self.db_manager.table_exists(table_name):
                logger.debug(f"Table {table_name} does not exist, will create and load")
                return False
            
            # Check if table has data
            if not self.db_manager.table_has_data(table_name):
                logger.debug(f"Table {table_name} exists but has no data, will load")
                return False
            
            # Table exists and has data, skip loading
            logger.info(f"Table {table_name} exists and has data, skipping load")
            return True
            
        except Exception as e:
            logger.error(f"Error checking table state for {table_name}: {e}")
            # If we can't determine the state, proceed with loading to be safe
            return False
    
    def _get_table_name_from_file(self, file_path: Path) -> str:
        """Extract table name from CSV filename and map to schema name."""
        # Remove extension and convert to lowercase
        base_name = file_path.stem.lower()
        
        # Replace spaces and special characters with underscores
        base_name = base_name.replace(' ', '_').replace('-', '_')
        
        # Map CSV filenames to schema table names
        # The schemas use 'enem_microdado_YYYY' format
        if 'microdados_enem_' in base_name:
            # Extract year from filename like 'microdados_enem_2001'
            year = base_name.split('_')[-1]
            table_name = f'enem_microdado_{year}'
            logger.debug(f"Mapped filename {base_name} to schema table {table_name}")
            return table_name
        else:
            # Fallback to original name if no mapping found
            logger.warning(f"No mapping found for filename {base_name}, using as-is")
            return base_name
    

    

    
    def _prepare_dataframe(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Prepare DataFrame for database insertion."""
        df_copy = df.copy()
        
        # Load schema for this table
        schema = self.db_manager.load_schema(table_name)
        columns = schema.get('columns', {})
        
        # Define missing value indicators common in ENEM data
        missing_indicators = ['*', '**', '***', '****', '*****', 'nan', 'NaN', 'NULL', 'null', 'None', '']
        
        logger.debug(f"Preparing DataFrame with {len(df_copy)} rows and {len(df_copy.columns)} columns")
        logger.debug(f"Schema types: {schema}")
        
        for column, pg_type in columns.items():
            if column not in df_copy.columns:
                logger.debug(f"Column {column} not found in DataFrame, skipping")
                continue
                
            pg_type = pg_type.upper()
            logger.debug(f"Processing column {column} with type {pg_type}")
            
            # First, replace missing indicators with NaN
            df_copy[column] = df_copy[column].replace(missing_indicators, pd.NA)
            
            if pg_type == 'BOOLEAN':
                df_copy[column] = df_copy[column].map({'1': 'true', '0': 'false'})
            elif pg_type in ('INTEGER', 'BIGINT'):
                # Convert to numeric, coercing errors to NaN
                df_copy[column] = pd.to_numeric(df_copy[column], errors='coerce')
                # Convert valid numbers to strings, NaN to \N
                df_copy[column] = df_copy[column].apply(
                    lambda x: str(int(x)) if pd.notna(x) else '\\N'
                )
            elif pg_type in ('DOUBLE PRECISION', 'DECIMAL', 'FLOAT'):
                # Convert to numeric, coercing errors to NaN
                df_copy[column] = pd.to_numeric(df_copy[column], errors='coerce')
                # Convert valid numbers to strings with proper decimal format, NaN to \N
                df_copy[column] = df_copy[column].apply(
                    lambda x: str(float(x)).replace(',', '.') if pd.notna(x) else '\\N'
                )
            else:
                # For TEXT columns, replace NaN with \N
                df_copy[column] = df_copy[column].fillna('\\N')
        
        # Final cleanup: replace any remaining NaN values with \N
        result = df_copy.replace({pd.NA: '\\N', 'nan': '\\N', 'None': '\\N'})
        
        logger.debug(f"DataFrame preparation completed")
        return result
    
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
    
    def check_tables_status(self, folder_path: str) -> dict:
        """
        Check the status of all tables that would be created from CSV files in the directory.
        
        Args:
            folder_path: Path to folder containing CSV files
            
        Returns:
            Dictionary with table status information
        """
        try:
            folder = Path(folder_path)
            if not folder.exists():
                logger.error(f"Folder does not exist: {folder_path}")
                return {'error': f'Folder does not exist: {folder_path}'}
            
            # Find all CSV files
            csv_files = list(folder.glob("*.csv"))
            if not csv_files:
                logger.warning("No CSV files found to check")
                return {'files_found': 0, 'tables': {}}
            
            logger.info(f"Checking status of {len(csv_files)} CSV files")
            
            table_status = {}
            for csv_file in csv_files:
                table_name = self._get_table_name_from_file(csv_file)
                
                try:
                    exists = self.db_manager.table_exists(table_name)
                    has_data = self.db_manager.table_has_data(table_name) if exists else False
                    
                    table_status[table_name] = {
                        'file': str(csv_file),
                        'exists': exists,
                        'has_data': has_data,
                        'will_skip': exists and has_data
                    }
                    
                except Exception as e:
                    logger.error(f"Error checking status for {table_name}: {e}")
                    table_status[table_name] = {
                        'file': str(csv_file),
                        'error': str(e)
                    }
            
            # Calculate summary
            total_files = len(csv_files)
            existing_tables = sum(1 for status in table_status.values() if status.get('exists', False))
            tables_with_data = sum(1 for status in table_status.values() if status.get('has_data', False))
            will_skip = sum(1 for status in table_status.values() if status.get('will_skip', False))
            
            summary = {
                'files_found': total_files,
                'existing_tables': existing_tables,
                'tables_with_data': tables_with_data,
                'will_skip': will_skip,
                'will_process': total_files - will_skip,
                'tables': table_status
            }
            
            logger.info(f"Table status summary: {will_skip} files will be skipped, {total_files - will_skip} files will be processed")
            return summary
            
        except Exception as e:
            logger.error(f"Error checking tables status: {e}")
            return {'error': str(e)}
    
    def close(self):
        """Close database connections."""
        if self.db_manager:
            self.db_manager.close() 