# Source Code Documentation

This directory contains the core source code for the ENEM Microdata ETL Pipeline. The code is organized into modular components that handle different aspects of the data processing pipeline.

## 📁 Module Overview

### Core ETL Components

- **`config.py`** - Unified configuration management
- **`database.py`** - Database operations and connection management
- **`downloader.py`** - File downloading from ENEM website
- **`extractor.py`** - ZIP file extraction and validation
- **`loader.py`** - Data loading into PostgreSQL database
- **`cleanup.py`** - File cleanup and disk management
- **`united_table_logic.py`** - United table creation and management

### Pipeline Orchestration

- **`etl_pipeline.py`** - Main ETL pipeline orchestration
- **`etl_functions.py`** - ETL utility functions
- **`etl_operators.py`** - Airflow custom operators

## 🔧 Configuration Management (`config.py`)

### Purpose

Provides a centralized configuration management system that loads settings from a unified YAML file with environment variable support.

### Key Features

- **Unified Configuration**: Single `config.yml` file as source of truth
- **Environment Variable Support**: `${VAR:-default}` substitution syntax
- **Validation**: Configuration validation and error checking
- **Reloading**: Dynamic configuration reloading capability

### Core Classes

#### `ConfigManager`

Main configuration manager class that handles:
- Loading configuration from YAML files
- Environment variable substitution
- Configuration validation
- Path resolution and management

```python
from src.config import config_manager

# Get configuration values
chunk_size = config_manager.get('application.chunk_size', 10000)
db_config = config_manager.get_database_config('etl')

# Validate configuration
if config_manager.validate():
    print("✅ Configuration is valid")
```

### Configuration Hierarchy

1. **Environment Variables** (`.env` file or system environment)
2. **Unified Configuration** (`config.yml` with variable substitution)
3. **Hardcoded defaults** (in `src/config.py`)

### Environment Variable Substitution

```yaml
# In config.yml
database:
  etl:
    host: ${DB_HOST:-localhost}
    port: ${DB_PORT:-5433}
    password: ${DB_PASSWORD}  # No default - must be set
```

## 🗄️ Database Operations (`database.py`)

### Purpose

Manages database connections and operations for the triple database architecture (ETL, Airflow, Metabase).

### Key Features

- **Triple Database Support**: Separate managers for ETL, Airflow, and Metabase databases
- **Connection Pooling**: Efficient database connection management
- **Transaction Support**: ACID-compliant database operations
- **Error Handling**: Comprehensive error handling and recovery

### Core Classes

#### `DatabaseManager`

Factory class for creating database managers:

```python
from src.database import DatabaseManager

# Create database managers
etl_db = DatabaseManager.create_etl_manager()
airflow_db = DatabaseManager.create_airflow_manager()
metabase_db = DatabaseManager.create_metabase_manager()
```

#### `DatabaseConnection`

Individual database connection manager:

```python
# Create table from DataFrame
etl_db.create_table('enem_microdado_2023', df, drop_if_exists=True)

# Insert data
etl_db.insert_data('enem_microdado_2023', df)

# Execute custom SQL
etl_db.execute_query("SELECT COUNT(*) FROM enem_microdado_2023")

# Close connection
etl_db.close()
```

### Database Architecture

1. **ETL Database (Port 5433)**
   - Stores processed ENEM microdata
   - Individual year tables: `enem_microdado_YYYY`
   - United table: `enem_microdado_2011_2023`

2. **Airflow Database (Port 5432)**
   - Stores Airflow metadata and DAG execution history
   - Task instances and execution logs
   - Variable and connection configurations

3. **Metabase Database (Port 5434)**
   - Stores Metabase metadata and dashboard configurations
   - User preferences and saved questions
   - Dashboard and collection metadata

## 📥 File Downloading (`downloader.py`)

### Purpose

Handles downloading of ENEM microdata files from the official INEP website.

### Key Features

- **Automated Downloads**: Downloads files for specified years
- **Progress Tracking**: Visual progress bars and download history
- **Error Recovery**: Retry logic for failed downloads
- **File Validation**: Checks file integrity and completeness

### Core Classes

#### `ENEMDownloader`

Main downloader class for ENEM files:

```python
from src.downloader import ENEMDownloader

# Initialize downloader
downloader = ENEMDownloader()

# Download files for specific years
downloader.download_all(years=['2022', '2023'])

# Download single year
downloader.download_year(2023)

# Check download history
history = downloader.get_download_history()
```

### Download Process

1. **URL Generation**: Constructs download URLs for specified years
2. **File Discovery**: Finds available files on the ENEM website
3. **Download Execution**: Downloads files with progress tracking
4. **Validation**: Verifies downloaded file integrity
5. **History Tracking**: Records download metadata

### Error Handling

- **Network Errors**: Automatic retry with exponential backoff
- **File Corruption**: MD5 checksum validation
- **Incomplete Downloads**: Resume capability for large files
- **Rate Limiting**: Respects server rate limits

## 📦 File Extraction (`extractor.py`)

### Purpose

Handles extraction of ZIP files containing ENEM microdata and validation of extracted content.

### Key Features

- **ZIP Extraction**: Extracts ZIP files to specified directories
- **File Validation**: Validates extracted file integrity
- **CSV Detection**: Identifies and validates CSV files
- **Error Handling**: Comprehensive error handling and recovery

### Core Classes

#### `ENEMExtractor`

Main extractor class for ENEM files:

```python
from src.extractor import ENEMExtractor

# Initialize extractor
extractor = ENEMExtractor()

# Extract all ZIP files
extractor.extract_all()

# Extract specific file
extractor.extract_file('downloads/MICRODADOS_ENEM_2023.zip')

# Validate extracted files
extractor.validate_extracted_files()
```

### Extraction Process

1. **File Discovery**: Finds ZIP files in downloads directory
2. **Extraction**: Extracts ZIP files to data directory
3. **Validation**: Validates extracted file structure
4. **CSV Detection**: Identifies and validates CSV files
5. **Cleanup**: Removes temporary files

### File Structure Validation

- **Directory Structure**: Validates expected directory layout
- **File Naming**: Checks file naming conventions
- **File Size**: Validates file sizes and completeness
- **Content Validation**: Basic CSV structure validation

## 📊 Data Loading (`loader.py`)

### Purpose

Handles loading of CSV data into PostgreSQL database with optimization and error handling.

### Key Features

- **Chunked Loading**: Processes large files in manageable chunks
- **Schema Management**: Uses predefined schemas for table creation
- **Performance Optimization**: Efficient data loading strategies
- **Error Recovery**: Handles loading errors and provides recovery options

### Core Classes

#### `ENEMLoader`

Main loader class for ENEM data:

```python
from src.loader import ENEMLoader

# Initialize loader
loader = ENEMLoader()

# Load all CSV files
loader.load_all_files("data/")

# Load specific file
loader.load_file("data/MICRODADOS_ENEM_2023.csv")

# Create united table
loader.create_united_table()

# Populate united table
loader.populate_united_table()

# Close connection
loader.close()
```

### Loading Process

1. **File Discovery**: Finds CSV files in specified directory
2. **Schema Loading**: Loads table schemas from configuration
3. **Table Creation**: Creates database tables with proper schema
4. **Data Loading**: Loads data in chunks for performance
5. **Index Creation**: Creates database indexes for query performance

### Performance Optimization

- **Chunked Processing**: Processes data in configurable chunks
- **Batch Inserts**: Uses batch inserts for better performance
- **Index Management**: Creates indexes after data loading
- **Memory Management**: Efficient memory usage for large datasets

## 🧹 File Cleanup (`cleanup.py`)

### Purpose

Manages cleanup of temporary files and disk space optimization.

### Key Features

- **Selective Cleanup**: Removes specific file types (CSV, ZIP)
- **Disk Usage Monitoring**: Tracks disk space usage
- **Safe Deletion**: Validates files before deletion
- **Space Reporting**: Reports freed space and remaining usage

### Core Classes

#### `CleanupManager`

Main cleanup manager class:

```python
from src.cleanup import CleanupManager

# Initialize cleanup manager
cleanup = CleanupManager()

# Clean up CSV files
result = cleanup.cleanup_csv_files()
print(f"Deleted {result['files_deleted']} CSV files")

# Clean up ZIP files
result = cleanup.cleanup_zip_files()
print(f"Deleted {result['files_deleted']} ZIP files")

# Clean up all temporary files
result = cleanup.cleanup_all_temp_files()
print(f"Total space freed: {result['total_space_freed_bytes']} bytes")

# Get disk usage information
usage = cleanup.get_disk_usage_info()
print(f"Downloads directory contains {usage['file_count']} files")
```

### Cleanup Operations

1. **CSV Cleanup**: Removes processed CSV files
2. **ZIP Cleanup**: Removes downloaded ZIP files
3. **Temporary Files**: Removes temporary processing files
4. **Log Cleanup**: Manages log file rotation and cleanup

### Safety Features

- **File Validation**: Validates files before deletion
- **Backup Options**: Optional backup before deletion
- **Dry Run Mode**: Preview cleanup operations
- **Size Limits**: Configurable size limits for cleanup

## 🗃️ United Table Logic (`united_table_logic.py`)

### Purpose

Manages the creation and population of the united table that combines ENEM data from multiple years.

### Key Features

- **Schema Management**: Uses predefined schemas for table structure
- **Data Integration**: Combines data from multiple year tables
- **Index Optimization**: Creates optimized indexes for performance
- **Progress Tracking**: Tracks population progress for large datasets

### Core Classes

#### `UnitedTableLogic`

Main united table logic class:

```python
from src.united_table_logic import UnitedTableLogic

# Initialize united table logic
logic = UnitedTableLogic()

# Get table information
info = logic.get_united_table_info()
print(f"United table will have {info['column_count']} columns")

# Create united table
success = logic.create_united_table(drop_if_exists=True)

# Populate united table
success = logic.populate_united_table()

# Create indexes
success = logic.create_united_table_indexes()

# Close connection
logic.close()
```

### United Table Process

1. **Schema Loading**: Loads unified schema from configuration
2. **Table Creation**: Creates table with proper structure
3. **Data Population**: Populates table from year-specific tables
4. **Index Creation**: Creates performance indexes
5. **Validation**: Validates data integrity and completeness

### Schema Management

- **Column Mapping**: Maps columns across different years
- **Type Consistency**: Ensures consistent data types
- **Index Strategy**: Optimizes indexes for common queries
- **Constraint Management**: Manages table constraints and relationships

## 🔄 ETL Pipeline (`etl_pipeline.py`)

### Purpose

Orchestrates the complete ETL process from download to database loading.

### Key Features

- **End-to-End Processing**: Complete pipeline from download to database
- **Configurable Years**: Processes specific years or all available years
- **Error Handling**: Comprehensive error handling and recovery
- **Progress Tracking**: Detailed progress reporting

### Core Functions

#### `run_etl_pipeline()`

Main ETL pipeline function:

```python
from src.etl_pipeline import run_etl_pipeline

# Run for all years
run_etl_pipeline()

# Run for specific years
run_etl_pipeline(years=['2022', '2023'])

# Skip download phase
run_etl_pipeline(skip_download=True)
```

### Pipeline Stages

1. **Download Stage**: Downloads files from ENEM website
2. **Extract Stage**: Extracts ZIP files to data directory
3. **Load Stage**: Loads data into PostgreSQL database
4. **United Table Stage**: Creates and populates united table
5. **Cleanup Stage**: Cleans up temporary files

### Configuration Options

- **Years**: Specific years to process
- **Skip Download**: Skip download if files exist
- **Chunk Size**: Data processing chunk size
- **Log Level**: Logging verbosity level

## 🔧 ETL Functions (`etl_functions.py`)

### Purpose

Provides utility functions for ETL operations and data processing.

### Key Features

- **Data Validation**: Validates data integrity and quality
- **Transformation**: Data transformation and cleaning functions
- **Utility Functions**: Common ETL utility functions
- **Error Handling**: Standardized error handling patterns

### Core Functions

```python
from src.etl_functions import (
    validate_csv_file,
    transform_data,
    clean_column_names,
    handle_missing_values
)

# Validate CSV file
is_valid = validate_csv_file("data/file.csv")

# Transform data
transformed_df = transform_data(df)

# Clean column names
clean_df = clean_column_names(df)

# Handle missing values
cleaned_df = handle_missing_values(df)
```

### Data Processing Functions

1. **Validation Functions**: Data quality and integrity checks
2. **Transformation Functions**: Data cleaning and transformation
3. **Utility Functions**: Common ETL operations
4. **Error Handling**: Standardized error handling

## 🎯 ETL Operators (`etl_operators.py`)

### Purpose

Provides custom Airflow operators for ETL operations.

### Key Features

- **Custom Operators**: Airflow operators for ETL tasks
- **Error Handling**: Built-in error handling and retry logic
- **Logging**: Comprehensive logging and monitoring
- **Integration**: Seamless integration with Airflow DAGs

### Core Operators

#### `ENEMDownloadOperator`

Downloads ENEM files:

```python
from src.etl_operators import ENEMDownloadOperator

download_task = ENEMDownloadOperator(
    task_id='download_enem_files',
    years=['2022', '2023'],
    dag=dag
)
```

#### `ENEMExtractOperator`

Extracts ZIP files:

```python
from src.etl_operators import ENEMExtractOperator

extract_task = ENEMExtractOperator(
    task_id='extract_enem_files',
    dag=dag
)
```

#### `ENEMLoadOperator`

Loads data into database:

```python
from src.etl_operators import ENEMLoadOperator

load_task = ENEMLoadOperator(
    task_id='load_enem_data',
    dag=dag
)
```

### Operator Features

- **Task Dependencies**: Automatic task dependency management
- **Error Handling**: Built-in error handling and retry logic
- **Progress Tracking**: Real-time progress monitoring
- **Resource Management**: Efficient resource usage

## 🧪 Testing

### Unit Testing

Each module includes comprehensive unit tests:

```bash
# Run unit tests
python -m pytest tests/unit/ -v

# Run specific module tests
python -m pytest tests/unit/test_database.py -v
```

### Integration Testing

Integration tests verify module interactions:

```bash
# Run integration tests
python -m pytest tests/integration/ -v
```

### Test Coverage

- **Unit Tests**: Individual module functionality
- **Integration Tests**: Module interaction testing
- **End-to-End Tests**: Complete pipeline testing
- **Performance Tests**: Performance and scalability testing

## 📈 Performance Considerations

### Optimization Strategies

1. **Chunked Processing**: Process large datasets in chunks
2. **Connection Pooling**: Efficient database connection management
3. **Batch Operations**: Use batch operations for better performance
4. **Index Management**: Optimize database indexes for queries

### Memory Management

- **Streaming**: Stream large files instead of loading entirely into memory
- **Garbage Collection**: Proper cleanup of large objects
- **Memory Monitoring**: Track memory usage during processing

### Database Optimization

- **Index Strategy**: Create appropriate indexes for common queries
- **Query Optimization**: Optimize database queries for performance
- **Connection Management**: Efficient connection pooling and management

## 🔒 Security Considerations

### Data Security

- **Input Validation**: Validate all inputs and file contents
- **SQL Injection Prevention**: Use parameterized queries
- **File Path Security**: Validate and sanitize file paths
- **Access Control**: Implement appropriate access controls

### Configuration Security

- **Credential Management**: Secure storage of database credentials
- **Environment Variables**: Use environment variables for sensitive data
- **File Permissions**: Proper file permissions for configuration files

## 🚨 Error Handling

### Error Types

1. **Configuration Errors**: Missing or invalid configuration
2. **Database Errors**: Connection and query errors
3. **File System Errors**: File access and permission errors
4. **Network Errors**: Download and connection errors

### Error Recovery

- **Retry Logic**: Automatic retry for transient errors
- **Graceful Degradation**: Continue processing when possible
- **Error Logging**: Comprehensive error logging and reporting
- **User Feedback**: Clear error messages and recovery suggestions

## 📚 Related Documentation

- **Main README.md** - Project overview and setup
- **config/README.md** - Configuration management
- **tests/README.md** - Testing documentation

- **scripts/README.md** - Utility scripts

## 🤝 Contributing

When contributing to the source code:

1. **Follow Standards**: Use established coding standards and patterns
2. **Add Documentation**: Include comprehensive docstrings
3. **Add Tests**: Create corresponding test cases
4. **Handle Errors**: Implement proper error handling
5. **Optimize Performance**: Consider performance implications
6. **Update Documentation**: Update relevant documentation 