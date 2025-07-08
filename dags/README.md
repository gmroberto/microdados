# Airflow DAGs Documentation

This directory contains Apache Airflow DAGs (Directed Acyclic Graphs) that orchestrate the ENEM Microdata ETL Pipeline. Each DAG represents a specific workflow or task in the data processing pipeline.

## 📁 DAGs Overview

### Main ETL Pipeline DAGs

- **`enem_etl_dag.py`** - Complete ETL pipeline orchestration
- **`enem_download_dag.py`** - File downloading workflow
- **`enem_extract_dag.py`** - ZIP file extraction workflow
- **`enem_load_dag.py`** - Data loading workflow

### United Table DAGs

- **`enem_create_united_table_dag.py`** - United table creation
- **`enem_populate_united_table_dag.py`** - United table population
- **`enem_create_indexes_dag.py`** - Database index creation

### Utility DAGs

- **`cleanup_csv_dag.py`** - CSV file cleanup operations
- **`enem_delete_zip_dag.py`** - ZIP file cleanup operations
- **`enem_pipeline_summary_dag.py`** - Pipeline summary and reporting

## 🚀 Getting Started

### Prerequisites

Before running the DAGs, ensure you have:

1. **Airflow Setup**: Airflow services running and accessible
2. **Database Access**: All three databases (ETL, Airflow, Metabase) running
3. **Configuration**: Proper configuration in `config/.env`
4. **Dependencies**: All required Python packages installed

### Accessing Airflow

```bash
# Start Airflow services
docker-compose up -d

# Access Airflow Web UI
# URL: http://localhost:8080
# Username: airflow
# Password: airflow
```

### Running DAGs

1. **Navigate to DAGs**: Go to the DAGs tab in Airflow Web UI
2. **Find DAG**: Locate the desired DAG in the list
3. **Trigger DAG**: Click "Trigger DAG" to start execution
4. **Monitor Progress**: Watch the execution in the Graph view

## 🔄 Main ETL Pipeline (`enem_etl_dag.py`)

### Purpose

Orchestrates the complete ETL process from download to database loading, including united table creation and cleanup operations.

### DAG Structure

```
enem_etl_pipeline_advanced
├── download_enem_files
├── extract_enem_files
├── load_enem_data
├── create_united_table
├── populate_united_table
├── create_indexes
├── cleanup_csv_files
└── cleanup_zip_files
```

### Task Dependencies

```
download_enem_files → extract_enem_files → load_enem_data
                                        ↓
create_united_table → populate_united_table → create_indexes
                                        ↓
cleanup_csv_files ← cleanup_zip_files
```

### Configuration

The DAG uses Airflow variables for configuration:

- `enem_years`: List of years to process
- `chunk_size`: Data processing chunk size
- `skip_download`: Whether to skip download phase
- `create_united_table`: Whether to create united table

### Example Usage

```python
# Trigger DAG with specific parameters
from airflow.models import Variable

# Set variables
Variable.set("enem_years", "['2022', '2023']")
Variable.set("chunk_size", "10000")
Variable.set("skip_download", "false")

# Trigger DAG
# Use Airflow Web UI or API to trigger the DAG
```

### Expected Execution Time

- **Small Dataset** (1-2 years): 30-60 minutes
- **Medium Dataset** (5-10 years): 2-4 hours
- **Large Dataset** (All years): 6-12 hours

## 📥 Download DAG (`enem_download_dag.py`)

### Purpose

Handles downloading of ENEM microdata files from the official INEP website.

### DAG Structure

```
enem_download_pipeline
└── download_enem_files
```

### Task Details

#### `download_enem_files`

- **Operator**: `ENEMDownloadOperator`
- **Purpose**: Downloads ENEM files for specified years
- **Parameters**:
  - `years`: List of years to download
  - `base_url`: ENEM data base URL
  - `download_dir`: Directory to save files

### Configuration

- **Years**: Configure via Airflow variables
- **Base URL**: ENEM official data URL
- **Download Directory**: Local directory for file storage

### Error Handling

- **Retry Logic**: Automatic retry for network errors
- **File Validation**: Checks downloaded file integrity
- **Progress Tracking**: Real-time download progress

## 📦 Extract DAG (`enem_extract_dag.py`)

### Purpose

Handles extraction of ZIP files containing ENEM microdata.

### DAG Structure

```
enem_extract_pipeline
└── extract_enem_files
```

### Task Details

#### `extract_enem_files`

- **Operator**: `ENEMExtractOperator`
- **Purpose**: Extracts ZIP files to data directory
- **Parameters**:
  - `download_dir`: Directory containing ZIP files
  - `extract_dir`: Directory to extract files to

### Extraction Process

1. **File Discovery**: Finds ZIP files in download directory
2. **Extraction**: Extracts files to data directory
3. **Validation**: Validates extracted file structure
4. **Cleanup**: Removes temporary extraction files

### Error Handling

- **Corrupted Files**: Handles corrupted ZIP files
- **Disk Space**: Checks available disk space
- **File Permissions**: Handles permission issues

## 📊 Load DAG (`enem_load_dag.py`)

### Purpose

Handles loading of CSV data into PostgreSQL database.

### DAG Structure

```
enem_load_pipeline
└── load_enem_data
```

### Task Details

#### `load_enem_data`

- **Operator**: `ENEMLoadOperator`
- **Purpose**: Loads CSV data into database tables
- **Parameters**:
  - `data_dir`: Directory containing CSV files
  - `chunk_size`: Data processing chunk size
  - `schema_file`: Database schema file path

### Loading Process

1. **File Discovery**: Finds CSV files in data directory
2. **Schema Loading**: Loads table schemas from configuration
3. **Table Creation**: Creates database tables
4. **Data Loading**: Loads data in chunks
5. **Index Creation**: Creates database indexes

### Performance Optimization

- **Chunked Processing**: Processes data in configurable chunks
- **Batch Inserts**: Uses batch inserts for better performance
- **Memory Management**: Efficient memory usage for large datasets

## 🗃️ United Table DAGs

### Create United Table (`enem_create_united_table_dag.py`)

#### Purpose

Creates the united table that combines ENEM data from multiple years.

#### DAG Structure

```
enem_create_united_table_pipeline
└── create_united_table
```

#### Task Details

- **Operator**: `ENEMUnitedTableOperator`
- **Purpose**: Creates united table with proper schema
- **Parameters**:
  - `table_name`: United table name
  - `schema_file`: Schema file path
  - `drop_if_exists`: Whether to drop existing table

### Populate United Table (`enem_populate_united_table_dag.py`)

#### Purpose

Populates the united table with data from year-specific tables.

#### DAG Structure

```
enem_populate_united_table_pipeline
└── populate_united_table
```

#### Task Details

- **Operator**: `ENEMUnitedTableOperator`
- **Purpose**: Populates united table with data
- **Parameters**:
  - `table_name`: United table name
  - `years`: Years to include in united table

### Create Indexes (`enem_create_indexes_dag.py`)

#### Purpose

Creates database indexes for the united table.

#### DAG Structure

```
enem_create_indexes_pipeline
└── create_indexes
```

#### Task Details

- **Operator**: `ENEMUnitedTableOperator`
- **Purpose**: Creates performance indexes
- **Parameters**:
  - `table_name`: Table to create indexes for
  - `index_config`: Index configuration

## 🧹 Cleanup DAGs

### CSV Cleanup (`cleanup_csv_dag.py`)

#### Purpose

Removes processed CSV files to free up disk space.

#### DAG Structure

```
enem_cleanup_csv_pipeline
└── cleanup_csv_files
```

#### Task Details

- **Operator**: `ENEMCleanupOperator`
- **Purpose**: Removes CSV files from data directory
- **Parameters**:
  - `data_dir`: Directory containing CSV files
  - `file_pattern`: CSV file pattern to match

### ZIP Cleanup (`enem_delete_zip_dag.py`)

#### Purpose

Removes downloaded ZIP files to free up disk space.

#### DAG Structure

```
enem_delete_zip_pipeline
└── delete_zip_files
```

#### Task Details

- **Operator**: `ENEMCleanupOperator`
- **Purpose**: Removes ZIP files from download directory
- **Parameters**:
  - `download_dir`: Directory containing ZIP files
  - `file_pattern`: ZIP file pattern to match

## 📈 Pipeline Summary (`enem_pipeline_summary_dag.py`)

### Purpose

Generates summary reports and statistics about the ETL pipeline execution.

### DAG Structure

```
enem_pipeline_summary_pipeline
└── generate_pipeline_summary
```

### Task Details

- **Operator**: `ENEMSummaryOperator`
- **Purpose**: Generates pipeline execution summary
- **Parameters**:
  - `summary_type`: Type of summary to generate
  - `output_format`: Output format (JSON, CSV, etc.)

### Summary Information

- **Execution Statistics**: Task execution times and success rates
- **Data Statistics**: Record counts and data quality metrics
- **Resource Usage**: Memory and disk usage statistics
- **Error Reports**: Summary of errors and warnings

## 🔧 Custom Operators

### ENEMDownloadOperator

Downloads ENEM files from the official website.

```python
from src.etl_operators import ENEMDownloadOperator

download_task = ENEMDownloadOperator(
    task_id='download_enem_files',
    years=['2022', '2023'],
    base_url='https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem',
    download_dir='downloads/',
    dag=dag
)
```

### ENEMExtractOperator

Extracts ZIP files containing ENEM data.

```python
from src.etl_operators import ENEMExtractOperator

extract_task = ENEMExtractOperator(
    task_id='extract_enem_files',
    download_dir='downloads/',
    extract_dir='data/',
    dag=dag
)
```

### ENEMLoadOperator

Loads CSV data into PostgreSQL database.

```python
from src.etl_operators import ENEMLoadOperator

load_task = ENEMLoadOperator(
    task_id='load_enem_data',
    data_dir='data/',
    chunk_size=10000,
    schema_file='config/schemas/enem_tables.yml',
    dag=dag
)
```

### ENEMUnitedTableOperator

Manages united table operations.

```python
from src.etl_operators import ENEMUnitedTableOperator

united_table_task = ENEMUnitedTableOperator(
    task_id='create_united_table',
    operation='create',
    table_name='enem_microdado_2011_2023',
    schema_file='config/schemas/enem_tables.yml',
    dag=dag
)
```

### ENEMCleanupOperator

Handles file cleanup operations.

```python
from src.etl_operators import ENEMCleanupOperator

cleanup_task = ENEMCleanupOperator(
    task_id='cleanup_csv_files',
    cleanup_type='csv',
    data_dir='data/',
    file_pattern='*.csv',
    dag=dag
)
```

## ⚙️ Configuration

### Airflow Variables

Configure DAGs using Airflow variables:

```python
# Set variables via Airflow Web UI or API
enem_years = ['2022', '2023']
chunk_size = 10000
skip_download = false
create_united_table = true
cleanup_after_load = true
```

### Environment Variables

DAGs use environment variables for sensitive configuration:

```bash
# Database credentials
DB_PASSWORD=your_etl_password
AIRFLOW_DB_PASSWORD=your_airflow_password
METABASE_DB_PASSWORD=your_metabase_password

# Secret keys
AIRFLOW__WEBSERVER__SECRET_KEY=your_secret_key
METABASE_ENCRYPTION_SECRET_KEY=your_metabase_key
```

### DAG Configuration

Each DAG can be configured independently:

- **Schedule**: Cron expressions for scheduling
- **Retries**: Number of retry attempts
- **Timeout**: Task timeout settings
- **Resources**: CPU and memory requirements

## 📊 Monitoring and Logging

### Task Monitoring

- **Task Status**: Real-time task execution status
- **Progress Tracking**: Detailed progress information
- **Error Reporting**: Comprehensive error messages
- **Performance Metrics**: Execution time and resource usage

### Logging

- **Task Logs**: Detailed logs for each task
- **Error Logs**: Error-specific logging
- **Performance Logs**: Performance and timing information
- **Audit Logs**: Pipeline execution audit trail

### Alerts and Notifications

- **Task Failures**: Email notifications for failed tasks
- **Performance Alerts**: Alerts for slow-running tasks
- **Resource Alerts**: Alerts for resource usage issues
- **Success Notifications**: Confirmations for successful runs

## 🚨 Error Handling

### Retry Logic

- **Automatic Retries**: Configurable retry attempts
- **Exponential Backoff**: Increasing delay between retries
- **Error Classification**: Different retry strategies for different errors
- **Manual Retry**: Manual retry capability for failed tasks

### Error Recovery

- **Graceful Degradation**: Continue processing when possible
- **Partial Success**: Handle partial task completion
- **Data Validation**: Validate data integrity after errors
- **Rollback Capability**: Rollback changes on critical errors

### Error Types

1. **Configuration Errors**: Missing or invalid configuration
2. **Database Errors**: Connection and query errors
3. **File System Errors**: File access and permission errors
4. **Network Errors**: Download and connection errors
5. **Resource Errors**: Memory and disk space issues

## 📈 Performance Optimization

### Task Optimization

- **Parallel Execution**: Execute independent tasks in parallel
- **Resource Allocation**: Optimize CPU and memory usage
- **Batch Processing**: Process data in optimal batch sizes
- **Caching**: Cache frequently accessed data

### Database Optimization

- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Optimize database queries
- **Index Management**: Proper index creation and maintenance
- **Transaction Management**: Efficient transaction handling

### Resource Management

- **Memory Usage**: Monitor and optimize memory usage
- **Disk Space**: Manage disk space efficiently
- **CPU Utilization**: Optimize CPU usage
- **Network Bandwidth**: Efficient network usage

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
- **Network Security**: Secure network connections

## 🧪 Testing DAGs

### Unit Testing

Test individual DAG components:

```bash
# Test DAG structure
python -m pytest tests/unit/test_dags.py -v

# Test specific DAG
python -m pytest tests/unit/test_dags.py::test_enem_etl_dag -v
```

### Integration Testing

Test DAG interactions:

```bash
# Test DAG integration
python -m pytest tests/integration/test_dag_integration.py -v
```

### DAG Validation

- **Structure Validation**: Validate DAG structure and dependencies
- **Configuration Validation**: Validate DAG configuration
- **Task Validation**: Validate individual task configurations
- **Integration Validation**: Validate DAG integration

## 📚 Related Documentation

- **Main README.md** - Project overview and setup
- **src/README.md** - Source code documentation
- **config/README.md** - Configuration management
- **tests/README.md** - Testing documentation

## 🤝 Contributing DAGs

When contributing new DAGs:

1. **Follow Standards**: Use established DAG patterns and conventions
2. **Add Documentation**: Include comprehensive docstrings
3. **Add Tests**: Create corresponding test cases
4. **Handle Errors**: Implement proper error handling
5. **Optimize Performance**: Consider performance implications
6. **Update Documentation**: Update relevant documentation

### DAG Template

```python
"""
ENEM [Specific Function] DAG

This DAG handles [specific functionality] for the ENEM microdata pipeline.

Features:
- [Feature 1]
- [Feature 2]
- [Feature 3]
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from src.etl_operators import ENEMCustomOperator

# DAG configuration
default_args = {
    'owner': 'enem-pipeline',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'enem_specific_function_pipeline',
    default_args=default_args,
    description='ENEM [Specific Function] Pipeline',
    schedule_interval=None,
    catchup=False,
    tags=['enem', 'etl', 'data-processing'],
)

# Define tasks
task1 = ENEMCustomOperator(
    task_id='task1',
    dag=dag,
)

task2 = ENEMCustomOperator(
    task_id='task2',
    dag=dag,
)

# Set task dependencies
task1 >> task2
``` 