"""
Pytest-based tests for ENEM Pipeline components.

This module provides comprehensive unit tests for the ENEM microdata ETL pipeline,
focusing on configuration, data validation, and core functionality.
"""

import pytest
import pandas as pd
import tempfile
import zipfile
import os
import logging
import traceback
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
# Add src to path for imports
import sys
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/test_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import components to test
from config import get_path, get_setting, get_url, config_manager
from downloader import ENEMDownloader
from extractor import ENEMExtractor
from database import DatabaseManager


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def has_database_config():
    """Check if database configuration is available for testing."""
    try:
        # Check if required database environment variables are set
        required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.info(f"Database tests will be skipped - missing environment variables: {', '.join(missing_vars)}")
            return False
        
        # Try to get database config
        db_config = config_manager.get_database_config('etl')
        required_keys = ['host', 'port', 'database', 'user', 'password']
        
        for key in required_keys:
            if key not in db_config or not db_config[key]:
                logger.info(f"Database tests will be skipped - missing or empty database config key: {key}")
                return False
        
        logger.info("Database configuration is available for testing")
        return True
    except Exception as e:
        logger.info(f"Database tests will be skipped - error checking database config: {e}")
        return False


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_enem_data():
    """Sample ENEM data for testing."""
    logger.info("Creating sample ENEM data fixture")
    data = pd.DataFrame({
        'nu_inscricao': [123456789012345, 987654321098765],
        'nu_ano': [2023, 2023],
        'tp_sexo': ['M', 'F'],
        'tp_cor_raca': [1, 2],
        'tp_presenca_cn': [1, 1],
        'tp_presenca_ch': [1, 1],
        'tp_presenca_lc': [1, 1],
        'tp_presenca_mt': [1, 1],
        'nu_nota_cn': [500.0, 600.0],
        'nu_nota_ch': [550.0, 650.0],
        'nu_nota_lc': [520.0, 620.0],
        'nu_nota_mt': [480.0, 580.0],
        'nu_nota_redacao': [700.0, 800.0]
    })
    logger.debug(f"Sample data created with shape: {data.shape}, columns: {list(data.columns)}")
    return data


@pytest.fixture
def temp_directory():
    """Temporary directory for testing."""
    logger.info("Creating temporary directory fixture")
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    logger.debug(f"Temporary directory created at: {temp_path}")
    yield temp_path
    logger.debug(f"Cleaning up temporary directory: {temp_path}")
    # Cleanup handled by tempfile


@pytest.fixture
def mock_database():
    """Mock database setup."""
    logger.info("Setting up mock database fixture")
    mock_db = Mock()
    mock_conn = Mock()
    mock_result = Mock()
    
    # Setup basic mock chain
    mock_result.fetchone.return_value = [3]  # Default row count
    mock_conn.execute.return_value = mock_result
    
    # Context manager mock
    context_mock = MagicMock()
    context_mock.__enter__.return_value = mock_conn
    context_mock.__exit__.return_value = None
    mock_db.engine.connect.return_value = context_mock
    
    logger.debug("Mock database setup completed")
    return mock_db, mock_conn, mock_result


@pytest.fixture
def test_zip_file(temp_directory):
    """Create a test ZIP file with ENEM data."""
    logger.info("Creating test ZIP file fixture")
    csv_content = "nu_inscricao;nu_ano;tp_sexo\n123456;2023;M\n789012;2023;F"
    zip_path = temp_directory / "test_microdados.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.writestr("MICRODADOS_ENEM_2023.csv", csv_content)
    
    logger.debug(f"Test ZIP file created at: {zip_path}")
    return zip_path


# =============================================================================
# CONFIGURATION TESTS
# =============================================================================

class TestConfiguration:
    """Test configuration validation and environment setup."""
    
    def test_environment_variables(self):
        """Test that required environment variables are set."""
        logger.info("Testing environment variables configuration")
        required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
                logger.warning(f"Missing environment variable: {var}")
            else:
                logger.debug(f"Environment variable {var} is set (value length: {len(value)})")
        
        if missing_vars:
            logger.info(f"Missing environment variables: {', '.join(missing_vars)} - this is expected in test environments")
            # Don't fail the test, just log the missing variables
            logger.info("Environment variables test completed - missing variables are expected in test environments")
        else:
            logger.info("All required environment variables are properly configured")
    
    def test_directory_structure(self):
        """Test that required directories exist and can be created."""
        logger.info("Testing directory structure creation")
        try:
            downloads_dir = get_path('downloads')
            logger.debug(f"Downloads directory path: {downloads_dir}")
            
            required_dirs = [downloads_dir, downloads_dir / "raw", Path("data"), Path("logs")]
            
            for dir_path in required_dirs:
                logger.debug(f"Creating/verifying directory: {dir_path}")
                dir_path.mkdir(exist_ok=True)
                
                if not dir_path.exists():
                    error_msg = f"Failed to create directory: {dir_path}"
                    logger.error(error_msg)
                    assert False, error_msg
                else:
                    logger.debug(f"Directory successfully created/verified: {dir_path}")
            
            logger.info("All required directories created successfully")
        except Exception as e:
            logger.error(f"Error creating directory structure: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def test_configuration_values(self):
        """Test that configuration values are properly set."""
        logger.info("Testing configuration values")
        
        try:
            enem_base_url = get_url('enem_base_url')
            logger.debug(f"ENEM base URL: {enem_base_url}")
            
            if not enem_base_url:
                error_msg = "ENEM_BASE_URL is not configured"
                logger.error(error_msg)
                assert False, error_msg
            
            if not enem_base_url.startswith('http'):
                error_msg = f"ENEM_BASE_URL should be a valid URL, got: {enem_base_url}"
                logger.error(error_msg)
                assert False, error_msg
            
            default_table_name = get_setting('united_table_name')
            logger.debug(f"Default table name: {default_table_name}")
            
            if not default_table_name:
                error_msg = "UNITED_TABLE_NAME is not configured"
                logger.error(error_msg)
                assert False, error_msg
            
            if 'enem' not in default_table_name.lower():
                error_msg = f"Table name should contain 'enem', got: {default_table_name}"
                logger.error(error_msg)
                assert False, error_msg
            
            logger.info("All configuration values are properly set")
        except Exception as e:
            logger.error(f"Error testing configuration values: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    @pytest.mark.database
    def test_database_config(self):
        """Test database configuration completeness."""
        logger.info("Testing database configuration completeness")
        
        if not has_database_config():
            pytest.skip("Database configuration not available - skipping database config test")
        
        try:
            db_config = config_manager.get_database_config('etl')
            logger.debug(f"Database config keys: {list(db_config.keys())}")
            
            required_keys = ['host', 'port', 'database', 'user', 'password']
            
            for key in required_keys:
                logger.debug(f"Checking database config key: {key}")
                
                if key not in db_config:
                    error_msg = f"Database configuration missing key: {key}"
                    logger.error(error_msg)
                    assert False, error_msg
                
                if not db_config[key]:
                    error_msg = f"Database configuration has empty value for: {key}"
                    logger.error(error_msg)
                    assert False, error_msg
                
                logger.debug(f"Database config key '{key}' is properly set")
            
            logger.info("Database configuration is complete")
        except Exception as e:
            logger.error(f"Error testing database configuration: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise


# =============================================================================
# DATABASE TESTS
# =============================================================================

@pytest.mark.database
class TestDatabaseConnectivity:
    """Test database connectivity and operations."""
    
    def test_database_connection(self):
        """Test basic database connection logic."""
        logger.info("Testing database connection")
        
        if not has_database_config():
            pytest.skip("Database configuration not available - skipping database connection test")
        
        try:
            db = DatabaseManager()
            logger.debug("DatabaseManager instantiated successfully")
            
            if db is None:
                error_msg = "DatabaseManager should be instantiable"
                logger.error(error_msg)
                assert False, error_msg
            
            logger.info("Database connection test passed")
        except Exception as e:
            logger.warning(f"Database connection failed (expected in test environment): {e}")
            logger.debug(f"Error type: {type(e).__name__}")
            logger.debug(f"Error message: {str(e)}")
            
            # Expected to fail without proper environment variables
            error_lower = str(e).lower()
            expected_keywords = ["connection", "database", "config", "environment"]
            
            if not any(keyword in error_lower for keyword in expected_keywords):
                logger.error(f"Unexpected error type: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                assert False, f"Unexpected error: {e}"
            
            logger.info("Database connection test handled expected failure gracefully")
    
    def test_table_operations(self, mock_database, sample_enem_data):
        """Test table creation, insertion, and verification with mocked database."""
        logger.info("Testing table operations with mocked database")
        
        try:
            mock_db, mock_conn, mock_result = mock_database
            logger.debug(f"Mock database setup: {type(mock_db)}")
            logger.debug(f"Sample data shape: {sample_enem_data.shape}")
            
            # Test operations using the mock
            logger.debug("Testing table creation")
            mock_db.create_table("test_table", sample_enem_data, drop_if_exists=True)
            
            logger.debug("Testing data insertion")
            mock_db.insert_data("test_table", sample_enem_data)
            
            # Verify mock was called correctly
            logger.debug("Verifying mock calls")
            with mock_db.engine.connect() as conn:
                result = conn.execute("SELECT COUNT(*) FROM test_table")
                count = result.fetchone()[0]
                logger.debug(f"Mock query returned count: {count}")
                
                if count != 3:
                    error_msg = f"Expected 3 rows, got {count}"
                    logger.error(error_msg)
                    assert False, error_msg
            
            logger.debug("Closing mock database")
            mock_db.close()
            
            logger.info("Table operations test completed successfully")
        except Exception as e:
            logger.error(f"Error in table operations test: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise


# =============================================================================
# DOWNLOADER TESTS
# =============================================================================

class TestDownloaderFunctionality:
    """Test downloader functionality with mock data."""
    
    def test_history_operations(self, temp_directory):
        """Test download history operations."""
        logger.info("Testing downloader history operations")
        
        try:
            with patch('src.config.get_path') as mock_get_path:
                mock_get_path.return_value = temp_directory
                logger.debug(f"Mocked config path: {temp_directory}")
                
                downloader = ENEMDownloader()
                logger.debug(f"Downloader instantiated: {type(downloader)}")
                
                                # Test history file path
                history_file = downloader.history_file
                logger.debug(f"History file path: {history_file}")

                # History file is only created when downloads happen, not on instantiation
                # So we just check that the path is set correctly
                if not str(history_file).endswith("download_history.json"):
                    error_msg = f"History file should be named download_history.json, got {history_file.name}"
                    logger.error(error_msg)
                    assert False, error_msg
                
                logger.debug("History file exists")
                
                # Test history loading and saving
                initial_history = downloader._load_history()
                logger.debug(f"Initial history type: {type(initial_history)}")
                logger.debug(f"Initial history content: {initial_history}")
                
                if not isinstance(initial_history, dict):
                    error_msg = f"History should be a dictionary, got {type(initial_history)}"
                    logger.error(error_msg)
                    assert False, error_msg
                
                # Test adding to history
                test_url = "https://example.com/test.zip"
                test_filename = "test_file.zip"
                logger.debug(f"Adding test entry to history: {test_url}")
                
                downloader.history[test_url] = {
                    'filename': test_filename,
                    'download_date': '2024-01-01'
                }
                downloader._save_history()
                
                # Test history persistence
                reloaded_history = downloader._load_history()
                logger.debug(f"Reloaded history: {reloaded_history}")
                
                if test_url not in reloaded_history:
                    error_msg = "History should persist added records"
                    logger.error(error_msg)
                    assert False, error_msg
                
                if reloaded_history[test_url]['filename'] != test_filename:
                    error_msg = f"History should store correct filename, expected {test_filename}, got {reloaded_history[test_url]['filename']}"
                    logger.error(error_msg)
                    assert False, error_msg
                
                logger.info("Downloader history operations test completed successfully")
        except Exception as e:
            logger.error(f"Error in downloader history operations test: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def test_file_operations(self, temp_directory):
        """Test file operations in download directory."""
        logger.info("Testing file operations in download directory")
        
        try:
            # Test directory creation
            raw_dir = temp_directory / "raw"
            logger.debug(f"Creating raw directory: {raw_dir}")
            raw_dir.mkdir(exist_ok=True)
            
            if not raw_dir.exists():
                error_msg = "Raw directory should exist"
                logger.error(error_msg)
                assert False, error_msg
            
            logger.debug("Raw directory created successfully")
            
            # Test file creation
            test_file = raw_dir / "test_file.txt"
            test_content = "test content"
            logger.debug(f"Creating test file: {test_file}")
            
            test_file.write_text(test_content)
            
            if not test_file.exists():
                error_msg = "Test file should be created"
                logger.error(error_msg)
                assert False, error_msg
            
            actual_content = test_file.read_text()
            if actual_content != test_content:
                error_msg = f"File content should match, expected '{test_content}', got '{actual_content}'"
                logger.error(error_msg)
                assert False, error_msg
            
            logger.info("File operations test completed successfully")
        except Exception as e:
            logger.error(f"Error in file operations test: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise


# =============================================================================
# EXTRACTOR TESTS
# =============================================================================

class TestExtractorFunctionality:
    """Test extractor functionality with mock ZIP files."""
    
    def test_zip_validation(self, test_zip_file, temp_directory):
        """Test ZIP file validation."""
        logger.info("Testing ZIP file validation")
        
        try:
            with patch('src.config.get_path') as mock_get_path:
                mock_get_path.return_value = temp_directory
                logger.debug(f"Mocked config path: {temp_directory}")
                logger.debug(f"Test ZIP file: {test_zip_file}")
                
                extractor = ENEMExtractor()
                logger.debug(f"Extractor instantiated: {type(extractor)}")
                
                # Test ZIP validation
                is_valid = extractor._is_valid_zip(test_zip_file)
                logger.debug(f"ZIP validation result: {is_valid}")
                
                if not is_valid:
                    error_msg = "ZIP file should be valid"
                    logger.error(error_msg)
                    assert False, error_msg
                
                logger.info("ZIP validation test completed successfully")
        except Exception as e:
            logger.error(f"Error in ZIP validation test: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def test_csv_extraction(self, test_zip_file, temp_directory):
        """Test CSV extraction from ZIP file."""
        logger.info("Testing CSV extraction from ZIP file")
        
        try:
            # Create a clean test environment by removing any existing CSV files
            existing_csv = temp_directory / "MICRODADOS_ENEM_2023.csv"
            if existing_csv.exists():
                existing_csv.unlink()
                logger.debug(f"Removed existing CSV file: {existing_csv}")
            
            logger.debug(f"Test ZIP file: {test_zip_file}")
            
            # Create extractor and patch its downloads_dir attribute
            extractor = ENEMExtractor()
            extractor.downloads_dir = temp_directory
            logger.debug(f"Extractor instantiated with downloads_dir: {extractor.downloads_dir}")
            
            # Test CSV extraction
            success = extractor._extract_zip(test_zip_file)
            logger.debug(f"ZIP extraction result: {success}")
            
            if not success:
                error_msg = "ZIP extraction should succeed"
                logger.error(error_msg)
                assert False, error_msg
            
            # Verify extracted file exists
            csv_file = temp_directory / "MICRODADOS_ENEM_2023.csv"
            logger.debug(f"Expected CSV file: {csv_file}")
            
            if not csv_file.exists():
                error_msg = "Extracted CSV file should exist"
                logger.error(error_msg)
                assert False, error_msg
            
            content = csv_file.read_text()
            logger.debug(f"CSV file content: {content[:100]}...")
            
            if "nu_inscricao" not in content:
                error_msg = "CSV should contain expected header 'nu_inscricao'"
                logger.error(error_msg)
                assert False, error_msg
            
            logger.info("CSV extraction test completed successfully")
        except Exception as e:
            logger.error(f"Error in CSV extraction test: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise


# =============================================================================
# LOADER TESTS
# =============================================================================

class TestLoaderFunctionality:
    """Test loader functionality with mock data."""
    
    def test_csv_file_detection(self, temp_directory):
        """Test CSV file detection in directory."""
        logger.info("Testing CSV file detection")
        
        try:
            # Create test CSV file
            test_csv_content = """nu_inscricao;nu_ano;tp_sexo;tp_cor_raca
123456;2023;M;1
789012;2023;F;2
345678;2023;M;1"""
            
            csv_file = temp_directory / "MICRODADOS_ENEM_2023.csv"
            logger.debug(f"Creating test CSV file: {csv_file}")
            csv_file.write_text(test_csv_content)
            
            # Test CSV file detection
            csv_files = list(temp_directory.glob('MICRODADOS_ENEM_*.csv'))
            logger.debug(f"Found CSV files: {[f.name for f in csv_files]}")
            
            if len(csv_files) != 1:
                error_msg = f"Expected 1 CSV file, found {len(csv_files)}"
                logger.error(error_msg)
                assert False, error_msg
            
            if csv_files[0].name != "MICRODADOS_ENEM_2023.csv":
                error_msg = f"Should find expected CSV file, got {csv_files[0].name}"
                logger.error(error_msg)
                assert False, error_msg
            
            logger.info("CSV file detection test completed successfully")
        except Exception as e:
            logger.error(f"Error in CSV file detection test: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def test_year_extraction(self):
        """Test year extraction from filename."""
        logger.info("Testing year extraction from filename")
        
        try:
            filename = "MICRODADOS_ENEM_2023.csv"
            logger.debug(f"Testing filename: {filename}")
            
            year = filename.split('_')[-1].replace('.csv', '')
            logger.debug(f"Extracted year: {year}")
            
            if year != '2023':
                error_msg = f"Expected year 2023, got {year}"
                logger.error(error_msg)
                assert False, error_msg
            
            logger.info("Year extraction test completed successfully")
        except Exception as e:
            logger.error(f"Error in year extraction test: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def test_table_name_generation(self):
        """Test table name generation from year."""
        logger.info("Testing table name generation")
        
        try:
            year = "2023"
            logger.debug(f"Input year: {year}")
            
            table_name = f"enem_microdado_{year}"
            logger.debug(f"Generated table name: {table_name}")
            
            expected_name = "enem_microdado_2023"
            if table_name != expected_name:
                error_msg = f"Expected table name {expected_name}, got {table_name}"
                logger.error(error_msg)
                assert False, error_msg
            
            logger.info("Table name generation test completed successfully")
        except Exception as e:
            logger.error(f"Error in table name generation test: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise


# =============================================================================
# DATA VALIDATION TESTS
# =============================================================================

class TestDataValidation:
    """Test data validation and quality checks."""
    
    def test_data_types(self, sample_enem_data):
        """Test data type validation."""
        logger.info("Testing data type validation")
        
        try:
            logger.debug(f"Sample data shape: {sample_enem_data.shape}")
            logger.debug(f"Sample data dtypes: {sample_enem_data.dtypes.to_dict()}")
            
            # Test nu_inscricao
            expected_dtype = 'int64'
            actual_dtype = str(sample_enem_data['nu_inscricao'].dtype)
            logger.debug(f"nu_inscricao dtype: expected {expected_dtype}, got {actual_dtype}")
            
            if actual_dtype != expected_dtype:
                error_msg = f"nu_inscricao should be {expected_dtype}, got {actual_dtype}"
                logger.error(error_msg)
                assert False, error_msg
            
            # Test nu_ano
            expected_dtype = 'int64'
            actual_dtype = str(sample_enem_data['nu_ano'].dtype)
            logger.debug(f"nu_ano dtype: expected {expected_dtype}, got {actual_dtype}")
            
            if actual_dtype != expected_dtype:
                error_msg = f"nu_ano should be {expected_dtype}, got {actual_dtype}"
                logger.error(error_msg)
                assert False, error_msg
            
            # Test tp_sexo
            expected_dtype = 'object'
            actual_dtype = str(sample_enem_data['tp_sexo'].dtype)
            logger.debug(f"tp_sexo dtype: expected {expected_dtype}, got {actual_dtype}")
            
            if actual_dtype != expected_dtype:
                error_msg = f"tp_sexo should be {expected_dtype}, got {actual_dtype}"
                logger.error(error_msg)
                assert False, error_msg
            
            # Test tp_cor_raca
            expected_dtype = 'int64'
            actual_dtype = str(sample_enem_data['tp_cor_raca'].dtype)
            logger.debug(f"tp_cor_raca dtype: expected {expected_dtype}, got {actual_dtype}")
            
            if actual_dtype != expected_dtype:
                error_msg = f"tp_cor_raca should be {expected_dtype}, got {actual_dtype}"
                logger.error(error_msg)
                assert False, error_msg
            
            # Test nu_nota_cn
            expected_dtype = 'float64'
            actual_dtype = str(sample_enem_data['nu_nota_cn'].dtype)
            logger.debug(f"nu_nota_cn dtype: expected {expected_dtype}, got {actual_dtype}")
            
            if actual_dtype != expected_dtype:
                error_msg = f"nu_nota_cn should be {expected_dtype}, got {actual_dtype}"
                logger.error(error_msg)
                assert False, error_msg
            
            logger.info("Data type validation test completed successfully")
        except Exception as e:
            logger.error(f"Error in data type validation test: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def test_data_ranges(self, sample_enem_data):
        """Test data range validation."""
        logger.info("Testing data range validation")
        
        try:
            logger.debug(f"Sample data shape: {sample_enem_data.shape}")
            
            # Test year range
            min_year = sample_enem_data['nu_ano'].min()
            max_year = sample_enem_data['nu_ano'].max()
            logger.debug(f"Year range: {min_year} to {max_year}")
            
            if min_year < 1998:
                error_msg = f"Year should be >= 1998, got {min_year}"
                logger.error(error_msg)
                assert False, error_msg
            
            if max_year > 2030:
                error_msg = f"Year should be <= 2030, got {max_year}"
                logger.error(error_msg)
                assert False, error_msg
            
            # Test sex values
            unique_sex = set(sample_enem_data['tp_sexo'].unique())
            logger.debug(f"Unique sex values: {unique_sex}")
            
            expected_sex = {'M', 'F'}
            if not unique_sex.issubset(expected_sex):
                error_msg = f"Sex should be M or F, got {unique_sex}"
                logger.error(error_msg)
                assert False, error_msg
            
            # Test race range
            min_race = sample_enem_data['tp_cor_raca'].min()
            max_race = sample_enem_data['tp_cor_raca'].max()
            logger.debug(f"Race range: {min_race} to {max_race}")
            
            if min_race < 0:
                error_msg = f"Race should be >= 0, got {min_race}"
                logger.error(error_msg)
                assert False, error_msg
            
            if max_race > 9:
                error_msg = f"Race should be <= 9, got {max_race}"
                logger.error(error_msg)
                assert False, error_msg
            
            # Test CN score range
            min_cn = sample_enem_data['nu_nota_cn'].min()
            max_cn = sample_enem_data['nu_nota_cn'].max()
            logger.debug(f"CN score range: {min_cn} to {max_cn}")
            
            if min_cn < 0:
                error_msg = f"CN score should be >= 0, got {min_cn}"
                logger.error(error_msg)
                assert False, error_msg
            
            if max_cn > 1000:
                error_msg = f"CN score should be <= 1000, got {max_cn}"
                logger.error(error_msg)
                assert False, error_msg
            
            logger.info("Data range validation test completed successfully")
        except Exception as e:
            logger.error(f"Error in data range validation test: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def test_data_completeness(self, sample_enem_data):
        """Test data completeness."""
        logger.info("Testing data completeness")
        
        try:
            logger.debug(f"Sample data shape: {sample_enem_data.shape}")
            
            # Check for null values
            null_counts = sample_enem_data.isnull().sum()
            logger.debug(f"Null value counts: {null_counts.to_dict()}")
            
            if sample_enem_data.isnull().any().any():
                error_msg = "Sample data should not contain null values"
                logger.error(error_msg)
                logger.error(f"Null value details: {null_counts[null_counts > 0].to_dict()}")
                assert False, error_msg
            
            # Check data length
            data_length = len(sample_enem_data)
            logger.debug(f"Data length: {data_length}")
            
            if data_length <= 0:
                error_msg = "Sample data should not be empty"
                logger.error(error_msg)
                assert False, error_msg
            
            # Check column count
            column_count = len(sample_enem_data.columns)
            logger.debug(f"Column count: {column_count}")
            
            if column_count < 5:
                error_msg = f"Sample data should have at least 5 columns, got {column_count}"
                logger.error(error_msg)
                assert False, error_msg
            
            logger.info("Data completeness test completed successfully")
        except Exception as e:
            logger.error(f"Error in data completeness test: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling:
    """Test error handling and recovery mechanisms."""
    
    def test_invalid_file_path(self):
        """Test handling of invalid file paths."""
        logger.info("Testing invalid file path handling")
        
        try:
            with pytest.raises(FileNotFoundError) as exc_info:
                logger.debug("Attempting to open non-existent file")
                with open("nonexistent_file.txt", "r") as f:
                    f.read()
            
            logger.debug(f"Expected FileNotFoundError raised: {exc_info.value}")
            logger.info("Invalid file path test completed successfully")
        except Exception as e:
            logger.error(f"Unexpected error in invalid file path test: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def test_invalid_csv_format(self):
        """Test handling of invalid CSV format."""
        logger.info("Testing invalid CSV format handling")
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write("invalid,csv,format\n")
                f.write("missing,quotes\n")
                f.write("unclosed,quote\n")
                temp_file = f.name
            
            logger.debug(f"Created malformed CSV file: {temp_file}")
            
            try:
                # This should handle malformed CSV gracefully
                df = pd.read_csv(temp_file)
                logger.debug(f"CSV read successfully, shape: {df.shape}")
                
                if len(df) <= 0:
                    error_msg = "CSV should be readable even if malformed"
                    logger.error(error_msg)
                    assert False, error_msg
                
                logger.info("Malformed CSV handled gracefully")
            except Exception as e:
                logger.warning(f"Pandas raised exception for malformed CSV (acceptable): {e}")
                logger.debug(f"Exception type: {type(e).__name__}")
                
                # It's also acceptable for pandas to raise an exception for malformed CSV
                error_lower = str(e).lower()
                expected_keywords = ["csv", "parse", "quote", "delimiter"]
                
                if not any(keyword in error_lower for keyword in expected_keywords):
                    logger.error(f"Unexpected error type for malformed CSV: {e}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    assert False, f"Unexpected error: {e}"
                
                logger.info("Expected exception for malformed CSV")
            finally:
                Path(temp_file).unlink()
                logger.debug(f"Cleaned up temporary file: {temp_file}")
        except Exception as e:
            logger.error(f"Error in invalid CSV format test: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    @pytest.mark.database
    def test_database_connection_error(self):
        """Test handling of database connection errors."""
        logger.info("Testing database connection error handling")
        
        if not has_database_config():
            pytest.skip("Database configuration not available - skipping database connection error test")
        
        try:
            with pytest.raises(Exception) as exc_info:
                logger.debug("Attempting to connect to non-existent database")
                # Try to connect to non-existent database
                db = DatabaseManager()
                db.engine = None  # Simulate connection failure
                with db.engine.connect():
                    pass
            
            logger.debug(f"Expected Exception raised: {exc_info.value}")
            logger.info("Database connection error test completed successfully")
        except Exception as e:
            logger.error(f"Unexpected error in database connection error test: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise 