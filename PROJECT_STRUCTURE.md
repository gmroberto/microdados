# Project Structure

This document provides a detailed overview of the ENEM Microdata ETL Pipeline project structure, explaining the purpose and organization of each directory and file.

## 📁 Root Directory Structure

```
microdados/
├── 📁 config/                 # Configuration management
├── 📁 dags/                   # Airflow DAGs
├── 📁 data/                   # Data storage
├── 📁 downloads/              # Downloaded files (gitignored)

├── 📁 logs/                   # Log files (gitignored)
├── 📁 plugins/                # Airflow plugins
├── 📁 scripts/                # Utility scripts
├── 📁 src/                    # Core source code
├── 📁 tests/                  # Test suite
├── 📁 venv/                   # Virtual environment (gitignored)
├── 📄 .dockerignore           # Docker ignore patterns
├── 📄 .gitignore              # Git ignore patterns
├── 📄 .pre-commit-config.yaml # Pre-commit hooks configuration
├── 📄 Dockerfile              # Docker containerization
├── 📄 Makefile                # Development tasks and commands
├── 📄 README.md               # Main project documentation
├── 📄 PROJECT_STRUCTURE.md    # This file
├── 📄 docker-compose.yml      # Docker services orchestration
├── 📄 entrypoint.py           # Docker entry point
├── 📄 requirements.txt        # Production dependencies
├── 📄 requirements-test.txt   # Testing dependencies
├── 📄 TEST_CONSOLIDATION_SUMMARY.md  # Test consolidation details
└── 📄 TEST_DAG_REMOVAL_SUMMARY.md    # DAG removal details
```

## 🔧 Configuration Directory (`config/`)

### Purpose

Contains all configuration files for the project, including the unified configuration system, environment templates, and database schemas.

### Structure

```
config/
├── 📄 airflow_init.py         # Airflow initialization script
├── 📄 config.yml              # Unified configuration file
├── 📄 defaulted_columns.json  # Default column mappings
├── 📄 download_history.json   # Download tracking metadata
├── 📄 env.template            # Environment variables template
└── 📁 schemas/                # Database schema definitions
    └── 📄 enem_tables.yml     # ENEM table schemas
```

### Key Files

- **`config.yml`**: Single source of truth for all configuration settings
- **`env.template`**: Template for environment variables (copy to `.env`)
- **`airflow_init.py`**: Initializes Airflow variables and connections
- **`schemas/enem_tables.yml`**: Defines database table structures and indexes

## 🚀 Airflow DAGs Directory (`dags/`)

### Purpose

Contains Apache Airflow DAGs that orchestrate the ETL pipeline workflows.

### Structure

```
dags/
├── 📄 cleanup_csv_dag.py              # CSV file cleanup
├── 📄 enem_create_indexes_dag.py      # Database index creation
├── 📄 enem_create_united_table_dag.py # United table creation
├── 📄 enem_delete_zip_dag.py          # ZIP file cleanup
├── 📄 enem_download_dag.py            # File downloading
├── 📄 enem_etl_dag.py                 # Complete ETL pipeline
├── 📄 enem_extract_dag.py             # ZIP file extraction
├── 📄 enem_load_dag.py                # Data loading
├── 📄 enem_pipeline_summary_dag.py    # Pipeline summary
└── 📄 enem_populate_united_table_dag.py # United table population
```

### DAG Categories

1. **Main ETL Pipeline**: Complete end-to-end data processing
2. **Component DAGs**: Individual pipeline stages (download, extract, load)
3. **United Table DAGs**: Combined data table management
4. **Utility DAGs**: Cleanup and maintenance operations

## 📊 Data Directory (`data/`)

### Purpose

Stores processed data files and intermediate data products.

### Structure

```
data/
├── 📁 raw/                    # Raw extracted data
└── 📁 processed/              # Processed data files
```

### Usage

- **`raw/`**: Contains extracted CSV files from ZIP archives
- **`processed/`**: Contains transformed and cleaned data files

## 📥 Downloads Directory (`downloads/`)

### Purpose

Stores downloaded ENEM microdata files from the official INEP website.

### Structure

```
downloads/
├── 📄 MICRODADOS_ENEM_2023.zip
├── 📄 MICRODADOS_ENEM_2022.zip
└── 📄 ... (other year files)
```

### Notes

- This directory is gitignored to avoid committing large data files
- Contains ZIP files downloaded from the ENEM official website
- Files are automatically cleaned up after processing



## 📝 Logs Directory (`logs/`)

### Purpose

Stores application logs and execution history.

### Structure

```
logs/
├── 📄 airflow.log             # Airflow execution logs
├── 📄 etl.log                 # ETL pipeline logs
└── 📄 ... (other log files)
```

### Notes

- This directory is gitignored to avoid committing log files
- Contains detailed execution logs for debugging and monitoring
- Logs are rotated and managed automatically

## 🔌 Plugins Directory (`plugins/`)

### Purpose

Contains Airflow plugins and custom extensions.

### Structure

```
plugins/
└── 📄 (Airflow plugin files)
```

### Usage

- Custom Airflow operators and sensors
- Plugin configurations and extensions
- Airflow-specific customizations

## 🛠️ Scripts Directory (`scripts/`)

### Purpose

Contains utility scripts for setup, management, and maintenance tasks.

### Structure

```
scripts/
├── 📄 dev_setup.py            # Development environment setup
├── 📄 setup_env.py            # Environment configuration
└── 📄 start_airflow.py        # Airflow service management (in scripts/)
```

### Script Types

1. **Setup Scripts**: Environment and development setup
2. **Management Scripts**: Service and configuration management
3. **Utility Scripts**: Common maintenance tasks

## 💻 Source Code Directory (`src/`)

### Purpose

Contains the core source code for the ENEM ETL pipeline.

### Structure

```
src/
├── 📄 cleanup.py              # File cleanup operations
├── 📄 config.py               # Configuration management
├── 📄 database.py             # Database operations
├── 📄 downloader.py           # File downloading
├── 📄 etl_functions.py        # ETL utility functions
├── 📄 etl_operators.py        # Airflow custom operators
├── 📄 etl_pipeline.py         # Main ETL pipeline
├── 📄 extractor.py            # ZIP file extraction
├── 📄 loader.py               # Data loading
└── 📄 united_table_logic.py   # United table management
```

### Module Categories

1. **Core ETL Components**: Download, extract, load operations
2. **Configuration Management**: Unified configuration system
3. **Database Operations**: Triple database architecture support
4. **Pipeline Orchestration**: ETL pipeline coordination
5. **Utility Functions**: Common ETL operations and helpers

## 🧪 Tests Directory (`tests/`)

### Purpose

Contains comprehensive test suite for the ENEM ETL pipeline.

### Structure

```
tests/
├── 📄 run_tests.py            # Test runner and orchestration
├── 📄 README.md               # Testing documentation
└── 📁 unit/                   # Unit tests
    └── 📄 test_assertions.py  # Pytest-based unit tests
```

### Test Types

1. **Unit Tests**: Individual module and function testing
2. **Integration Tests**: Module interaction testing
3. **End-to-End Tests**: Complete pipeline testing
4. **Performance Tests**: Performance and scalability testing

## 🔧 Configuration Files

### Root Level Configuration

- **`.dockerignore`**: Files to exclude from Docker builds
- **`.gitignore`**: Files to exclude from version control
- **`.pre-commit-config.yaml`**: Pre-commit hooks configuration
- **`Dockerfile`**: Docker container definition
- **`docker-compose.yml`**: Multi-service Docker orchestration
- **`Makefile`**: Development tasks and automation
- **`requirements.txt`**: Production Python dependencies
- **`requirements-test.txt`**: Testing Python dependencies

### Key Configuration Files

#### Docker Configuration

- **`Dockerfile`**: Defines the Airflow container with ENEM ETL dependencies
- **`docker-compose.yml`**: Orchestrates all services (databases, Airflow, Metabase)
- **`entrypoint.py`**: Docker container entry point script

#### Development Configuration

- **`Makefile`**: Provides convenient commands for development tasks
- **`.pre-commit-config.yaml`**: Ensures code quality with pre-commit hooks
- **`requirements.txt`**: Lists all production dependencies
- **`requirements-test.txt`**: Lists testing and development dependencies

## 🗄️ Database Architecture

### Triple Database Design

The project uses three separate PostgreSQL databases:

1. **ETL Database (Port 5433)**
   - **Purpose**: Stores processed ENEM microdata
   - **Tables**: Individual year tables and united table
   - **User**: `enem_etl_user`

2. **Airflow Database (Port 5432)**
   - **Purpose**: Stores Airflow metadata and execution history
   - **Tables**: DAGs, tasks, variables, connections
   - **User**: `enem_user`

3. **Metabase Database (Port 5434)**
   - **Purpose**: Stores Metabase metadata and dashboard configurations
   - **Tables**: Dashboards, questions, collections
   - **User**: `metabase_user`

## 🔄 Data Flow

### ETL Pipeline Flow

```
1. Download → 2. Extract → 3. Load → 4. United Table → 5. Cleanup
```

1. **Download Stage**: Downloads ZIP files from ENEM website
2. **Extract Stage**: Extracts CSV files from ZIP archives
3. **Load Stage**: Loads CSV data into PostgreSQL database
4. **United Table Stage**: Creates combined table from multiple years
5. **Cleanup Stage**: Removes temporary files to free disk space

### File Processing Flow

```
ENEM Website → ZIP Files → CSV Files → Database Tables → United Table
```

## 🛡️ Security Considerations

### File Permissions

- Configuration files have restricted permissions
- Database credentials are stored in environment variables
- Log files are protected from unauthorized access

### Data Protection

- Sensitive data is not committed to version control
- Database connections use secure authentication
- File paths are validated to prevent path traversal attacks

## 📈 Performance Considerations

### Optimization Strategies

1. **Chunked Processing**: Large datasets processed in manageable chunks
2. **Connection Pooling**: Efficient database connection management
3. **Batch Operations**: Database operations optimized for performance
4. **Index Management**: Strategic database indexing for query performance

### Resource Management

- **Memory**: Efficient memory usage for large datasets
- **Disk Space**: Automatic cleanup of temporary files
- **CPU**: Parallel processing where possible
- **Network**: Optimized download and upload operations

## 🔍 Monitoring and Logging

### Logging Structure

- **Application Logs**: ETL pipeline execution logs
- **Airflow Logs**: Workflow execution and task logs
- **Database Logs**: Database operation logs
- **System Logs**: System and service logs

### Monitoring Points

- **Task Execution**: Individual task success/failure monitoring
- **Performance Metrics**: Execution time and resource usage
- **Data Quality**: Data validation and quality checks
- **System Health**: Service availability and performance

## 🚨 Error Handling

### Error Categories

1. **Configuration Errors**: Missing or invalid configuration
2. **Database Errors**: Connection and query errors
3. **File System Errors**: File access and permission errors
4. **Network Errors**: Download and connection errors
5. **Data Errors**: Data validation and processing errors

### Recovery Strategies

- **Automatic Retries**: Configurable retry logic for transient errors
- **Graceful Degradation**: Continue processing when possible
- **Error Logging**: Comprehensive error logging and reporting
- **Manual Recovery**: Manual intervention capabilities

## 📚 Documentation Structure

### Documentation Hierarchy

1. **Main README.md**: Project overview and quick start
2. **PROJECT_STRUCTURE.md**: This file - detailed project organization
3. **src/README.md**: Source code documentation
4. **dags/README.md**: Airflow DAGs documentation
5. **config/README.md**: Configuration management guide
6. **tests/README.md**: Testing documentation

8. **scripts/README.md**: Utility scripts documentation

### Documentation Standards

- **Comprehensive Coverage**: All components documented
- **Clear Structure**: Logical organization and navigation
- **Regular Updates**: Documentation kept current with code changes

## 🤝 Contributing Guidelines

### Development Workflow

1. **Fork Repository**: Create personal fork for development
2. **Create Branch**: Use feature branches for new development
3. **Follow Standards**: Adhere to coding and documentation standards
4. **Add Tests**: Include tests for new functionality
5. **Update Documentation**: Keep documentation current
6. **Submit PR**: Create pull request with comprehensive description

### Code Standards

- **Python PEP 8**: Follow Python style guidelines
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Comprehensive function and class documentation
- **Error Handling**: Proper error handling and logging
- **Testing**: Maintain high test coverage

### Documentation Standards

- **Clear Structure**: Logical organization and navigation
- **Regular Updates**: Keep documentation current
- **Comprehensive Coverage**: Document all components

## 📋 Maintenance Tasks

### Regular Maintenance

1. **Dependency Updates**: Keep dependencies current and secure
2. **Log Rotation**: Manage log file sizes and retention
3. **Database Maintenance**: Regular database optimization
4. **Security Updates**: Apply security patches and updates
5. **Documentation Updates**: Keep documentation current

### Performance Monitoring

1. **Resource Usage**: Monitor CPU, memory, and disk usage
2. **Database Performance**: Monitor query performance and optimization
3. **Pipeline Performance**: Track ETL pipeline execution times
4. **Error Rates**: Monitor error rates and patterns

### Backup and Recovery

1. **Configuration Backup**: Regular backup of configuration files
2. **Database Backup**: Regular database backups
3. **Code Backup**: Version control and regular commits
4. **Recovery Procedures**: Documented recovery procedures 