# ENEM Microdata ETL Pipeline

A comprehensive ETL pipeline for processing ENEM (Brazilian National High School Exam) microdata with Airflow integration, featuring a unified configuration system and robust data processing capabilities.

## 🚀 Project Status: READY FOR GITHUB

This project has been thoroughly reviewed, tested, and cleaned up. It is ready for immediate use by other developers.

### ✅ What's Included
- **Complete ETL Pipeline**: Download, extract, load, and process ENEM microdata (1998-2023)
- **Production-Ready Docker Setup**: Triple database architecture with Airflow and Metabase
- **Comprehensive Testing**: Unit, integration, and end-to-end test suites
- **Professional Documentation**: Complete guides and setup instructions
- **Secure Configuration**: Environment-based credential management
- **Cross-Platform Support**: Works on Windows, Linux, and macOS

### 🎯 Quick Start
1. Clone the repository
2. Copy `config/env.template` to `config/.env` and configure your database credentials
3. Run `docker-compose up -d`
4. Access Airflow at http://localhost:8080 and Metabase at http://localhost:3000

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Features](#features)
- [Quick Start](#quick-start)
- [Database Setup](#database-setup)
- [Metabase Integration](#metabase-integration)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Development](#development)
- [Documentation](#documentation)
- [Contributing](#contributing)

## 🎯 Overview

This project provides a robust ETL pipeline for processing ENEM microdata from 1998 to 2023. It includes automated downloading, data extraction, database loading, and comprehensive testing capabilities, all orchestrated through Apache Airflow. The pipeline features a unified configuration system that simplifies setup and maintenance.

### Key Highlights

- **Unified Configuration**: Single `config.yml` file with environment variable support
- **Triple Database Architecture**: Separate databases for Airflow metadata, ETL data, and Metabase
- **United Table Logic**: Combines data from multiple years into a single optimized table
- **Production-Ready**: Docker containerization with health checks and monitoring
- **Comprehensive Testing**: Unit, integration, and end-to-end test suites
- **Cross-Platform**: Works seamlessly on Windows, Linux, and macOS
- **Metabase Integration**: Built-in business intelligence dashboard

## 📁 Project Structure

```
microdados/
├── src/                    # Core ETL pipeline code
│   ├── config.py          # Unified configuration management
│   ├── database.py        # Database operations
│   ├── downloader.py      # File downloading
│   ├── extractor.py       # ZIP file extraction
│   ├── loader.py          # Data loading into database
│   ├── cleanup.py         # File cleanup operations
│   ├── united_table_logic.py  # United table creation
│   └── etl_pipeline.py    # Main ETL pipeline
├── dags/                  # Airflow DAGs
│   ├── enem_etl_dag.py   # Main ETL pipeline DAG
│   ├── enem_download_dag.py  # Download DAG
│   ├── enem_extract_dag.py   # Extract DAG
│   ├── enem_load_dag.py      # Load DAG
│   ├── enem_create_united_table_dag.py  # United table creation DAG
│   ├── enem_populate_united_table_dag.py  # United table population DAG
│   ├── enem_create_indexes_dag.py  # Database indexes DAG
│   ├── enem_pipeline_summary_dag.py  # Pipeline summary DAG
│   └── cleanup_csv_dag.py  # Cleanup operations DAG
├── tests/                 # Comprehensive test suite
│   ├── unit/             # Unit tests
│   └── run_tests.py      # Test runner
├── scripts/               # Utility scripts
├── config/                # Unified configuration
│   ├── config.yml        # Single configuration file
│   ├── env.template      # Environment variables template
│   ├── schemas/
│   │   └── enem_tables.yml  # Database table schemas
│   └── README.md         # Configuration documentation
├── data/                  # Data storage (created automatically)
├── downloads/             # Downloaded files (created automatically)
├── logs/                  # Log files (created automatically)
├── docker-compose.yml    # Development environment
├── Dockerfile            # Containerization
└── Makefile              # Development tasks
```

## ✨ Features

- **Unified Configuration System**: Single `config.yml` file with environment variable support
- **Automated Data Pipeline**: Complete ETL process from download to database
- **Airflow Integration**: Production-ready DAGs for orchestration
- **Triple Database Architecture**: Separate databases for Airflow, ETL data, and Metabase
- **United Table Logic**: Combines data from multiple years into a single optimized table
- **Metabase Integration**: Built-in business intelligence dashboard
- **Robust Error Handling**: Comprehensive error recovery and retry logic
- **Database Optimization**: Efficient data loading with chunked processing
- **Comprehensive Testing**: Unit, integration, and end-to-end tests
- **Cross-Platform Support**: Works on Windows, Linux, and macOS
- **Docker Containerization**: Complete development environment
- **Progress Tracking**: Detailed logging and progress monitoring
- **File Cleanup**: Automated cleanup of temporary files

## 🚀 Quick Start

### Prerequisites

- **Docker and Docker Compose** (recommended)
- **Python 3.8+** (for local development)
- **PostgreSQL** (if not using Docker)

### ⚠️ Production Considerations

**Storage Strategy**: The current setup uses Docker volumes to store downloaded CSV and ZIP files. For production environments, consider using object storage solutions like AWS S3, Google Cloud Storage, or Azure Blob Storage instead of Docker volumes. These services provide better scalability, durability, and cost-effectiveness for large datasets, though they are paid services.

**Error Handling**: The current Airflow DAGs use try/catch blocks that may cause tasks to succeed even when they fail to complete their intended operations. The next development priority is to implement proper error checking after each step to ensure the DAG stops execution when critical operations fail.

### 1. Clone and Setup

```bash
git clone <repository-url>
cd microdados
```

**⚠️ Windows Users**: Avoid placing this project in directories with special characters (spaces, accents, symbols). For best compatibility, consider placing it in the root of your C: drive (e.g., `C:\microdados`).

**Recommended Windows Path**: `C:\microdados`

### 2. Configure Environment

```bash
# Option 1: Use the automated setup script (recommended)
make setup-env

# Option 2: Manual setup
cp config/env.template config/.env
# Edit config/.env with your database credentials
```

**Important**: You must create and configure the `.env` file for the pipeline to work!

### 3. Start with Docker (Recommended)

```bash
# Start all services (simplified initialization)
docker-compose up -d

# Check services
docker-compose ps
```

**Simplified Setup**: The Docker initialization has been simplified. Database initialization and admin user creation now happen automatically when services start. No manual initialization steps required!

### 4. Access Web Interfaces

- **Airflow Web UI**: http://localhost:8080
  - Username: `airflow`
  - Password: `airflow`
- **Metabase Dashboard**: http://localhost:3000
  - First-time setup will guide you through configuration

### 5. Run the Pipeline

1. Navigate to the DAGs tab in Airflow
2. Find `enem_etl_pipeline_advanced`
3. Click "Trigger DAG" to start the pipeline

### Alternative: Local Development

```bash
# Install dependencies
make install-dev

# Run tests
make test

# Start Airflow locally
make airflow-start
```

## 🗄️ Database Setup

This project uses **three separate PostgreSQL databases**:

### 1. Airflow Database (Port 5432)
- **Purpose**: Stores Airflow metadata, DAGs, and task execution history
- **Database**: `airflow`
- **User**: `enem_user`
- **Password**: `enem_password`
- **Host**: `localhost` (external) / `postgres` (Docker internal)

### 2. ETL Database (Port 5433)
- **Purpose**: Stores the processed ENEM microdata and analysis tables
- **Database**: `enem_data`
- **User**: `enem_etl_user`
- **Password**: `enem_etl_password`
- **Host**: `localhost` (external) / `postgres-etl` (Docker internal)

### 3. Metabase Database (Port 5434)
- **Purpose**: Stores Metabase metadata and dashboard configurations
- **Database**: `metabase`
- **User**: `metabase_user`
- **Password**: `metabase_password`
- **Host**: `localhost` (external) / `postgres-metabase` (Docker internal)

### Database Configuration

The database configuration is managed through the unified `config/config.yml` file:

```yaml
database:
  etl:
    host: ${DB_HOST:-localhost}
    port: ${DB_PORT:-5433}
    database: ${DB_NAME:-enem_data}
    user: ${DB_USER:-enem_etl_user}
    password: ${DB_PASSWORD}
  
  airflow:
    host: ${AIRFLOW_DB_HOST:-localhost}
    port: ${AIRFLOW_DB_PORT:-5432}
    database: ${AIRFLOW_DB_NAME:-airflow}
    user: ${AIRFLOW_DB_USER:-enem_user}
    password: ${AIRFLOW_DB_PASSWORD}
  
  metabase:
    host: ${METABASE_DB_HOST:-localhost}
    port: ${METABASE_DB_PORT:-5434}
    database: ${METABASE_DB_NAME:-metabase}
    user: ${METABASE_DB_USER:-metabase_user}
    password: ${METABASE_DB_PASSWORD}
```

### Testing Database Connections

```bash
# Test database connections
make test-db

# Or run directly
python scripts/test_databases.py
```

### External Database Access

To connect to the databases from external tools:

- **Airflow Database**: `localhost:5432`
- **ETL Database**: `localhost:5433`
- **Metabase Database**: `localhost:5434`

Use the respective credentials for each database.

## 📊 Metabase Integration

### Connecting Metabase to the ETL Database

To connect Metabase to your ETL database for data analysis:

1. **Access Metabase**: Navigate to http://localhost:3000
2. **Complete Initial Setup**: Follow the first-time setup wizard
3. **Add Database Connection**:
   - Click "Add your data" → "Database"
   - Select "PostgreSQL" as the database type
   - Use these connection details:
     ```
     Host: localhost
     Port: 5433
     Database name: enem_data
     Username: enem_etl_user
     Password: enem_etl_password
     ```
4. **Test Connection**: Click "Test connection" to verify
5. **Save**: Click "Save" to add the database

### Available Data Tables

Once connected, you'll have access to:

- **Individual Year Tables**: `enem_microdado_YYYY` (e.g., `enem_microdado_2023`)
- **United Table**: `enem_microdado_2011_2023` (combined data from 2011-2023)
- **Analysis Tables**: Various aggregated and processed tables

### Creating Dashboards

1. **Create Questions**: Start by creating questions about your data
2. **Build Dashboards**: Combine multiple questions into dashboards
3. **Share Insights**: Share dashboards with your team

### Metabase Configuration

Metabase is pre-configured in the Docker setup with:

- **Port**: 3000
- **Database**: PostgreSQL on port 5434
- **Persistence**: Data is stored in Docker volumes
- **Health Checks**: Automatic monitoring and restart

## ⚙️ Configuration

### Unified Configuration System

This project uses a unified configuration system with a single `config/config.yml` file that supports environment variable substitution.

### Environment Variables

Create a `config/.env` file based on `config/env.template`:

```env
# REQUIRED - Database Credentials
DB_USER=enem_etl_user
DB_PASSWORD=your_etl_password_here
AIRFLOW_DB_USER=enem_user
AIRFLOW_DB_PASSWORD=your_airflow_password_here
METABASE_DB_USER=metabase_user
METABASE_DB_PASSWORD=your_metabase_password_here

# OPTIONAL - Override defaults
ENVIRONMENT=development
CHUNK_SIZE=10000
LOG_LEVEL=INFO
SKIP_DOWNLOAD=false
```

### Configuration Hierarchy

Configuration is loaded in the following priority order:

1. **Environment Variables** (`.env` file or system environment)
2. **Unified Configuration** (`config/config.yml` with variable substitution)
3. **Hardcoded defaults** (in `src/config.py`)

### Using Configuration in Code

```python
from src.config import config_manager

# Get configuration values
chunk_size = config_manager.get('application.chunk_size', 10000)
db_config = config_manager.get_database_config('etl')

# Validate configuration
if config_manager.validate():
    print("✅ Configuration is valid")
```

For detailed configuration documentation, see `config/README.md`.

## 🔧 Usage

### Basic Usage

```python
from src.etl_pipeline import run_etl_pipeline

# Run for all years
run_etl_pipeline()

# Run for specific years
run_etl_pipeline(years=['2022', '2023'])

# Skip download phase (if files already exist)
run_etl_pipeline(skip_download=True)
```

### United Table Functionality

The pipeline automatically creates a united table (`enem_microdado_2011_2023`) using the schema from `config/schemas/enem_tables.yml`.

```python
from src.united_table_logic import UnitedTableLogic

# Get information about the united table
logic = UnitedTableLogic()
info = logic.get_united_table_info()
print(f"United table has {info['column_count']} columns")

# Create and populate united table
logic.create_united_table(drop_if_exists=True)
logic.populate_united_table()
logic.create_united_table_indexes()
logic.close()
```

### File Cleanup

The project includes automated cleanup functionality:

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

### Individual Components

```python
# Download files
from src.downloader import ENEMDownloader
downloader = ENEMDownloader()
downloader.download_all(years=['2023'])

# Extract ZIP files
from src.extractor import ENEMExtractor
extractor = ENEMExtractor()
extractor.extract_all()

# Load data into database
from src.loader import ENEMLoader
loader = ENEMLoader()
loader.load_all_files("downloads/")
loader.close()
```

## 🧪 Testing

### Quick Test (No Database Required)

```bash
# Run basic tests (no database required)
python tests/run_tests.py

# Run only non-database tests
pytest -m "not database"

# Run with verbose output
python tests/run_tests.py --verbose

# Run specific test categories
python tests/run_tests.py --file test_assertions.py --class-name TestConfiguration
```

### Comprehensive Testing

```bash
# Run all tests including database (if configured)
python tests/run_tests.py --database

# Run only database tests
python tests/run_tests.py --database-only

# Run with coverage
python tests/run_tests.py --coverage

# Run with coverage (using pytest directly)
pytest tests/unit/test_assertions.py --cov=src --cov-report=html
```

### Test Categories

#### Unit Tests (No Database Required)
These tests can run without any database configuration:
```bash
# Run only unit tests
pytest -m "not database"

# Run specific test class
pytest tests/unit/test_assertions.py::TestConfiguration

# Run specific test method
pytest tests/unit/test_assertions.py::TestConfiguration::test_environment_variables
```

#### Database Tests (Optional)
These tests require database configuration:
```bash
# Run only database tests
pytest -m "database"

# Check database configuration
python tests/run_tests.py --check-config

# Run all tests including database (if configured)
python tests/run_tests.py --database
```

### Environment Variables for Database Tests

To run database tests, set these environment variables:

```bash
export DB_USER=your_username
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=your_database
```

Or create a `.env` file in the project root:
```env
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
```

### Test Structure

- **Unit Tests** (`tests/unit/test_assertions.py`): Comprehensive pytest-based tests with helper utilities
- **Database Tests**: Optional tests that require database configuration
- **Quick Tests**: Basic functionality validation for rapid feedback

### Testing Strategy

**✅ Pre-Deployment Testing:**
- Run tests before building/deploying Airflow
- Validate configuration and environment
- Ensure data pipeline integrity

**❌ No Production Testing:**
- Tests are not run in Airflow production environment
- Airflow is for orchestration, not testing
- Test failures should prevent deployment, not trigger production alerts

### Test Database Setup

Tests use separate test databases to avoid affecting production data:

```bash
# Test database connections
make test-db

# Run database tests
python -m pytest tests/integration/test_databases.py -v
```

For detailed testing documentation, see `tests/README.md`.

## 🧪 Testing Notes and Best Practices

### Isolating File System Operations in Tests

When writing tests for components that interact with the file system (such as the ENEMExtractor), it is crucial to ensure that tests do not interfere with real data or each other. Here are some important observations and best practices:

- **Patch Class Attributes, Not Just Config Functions:**
  - If a class (like `ENEMExtractor`) reads configuration (e.g., download directory) during initialization, patching config functions (like `get_path`) after the class is instantiated will have no effect. The class will already have stored the original value.
  - **Best Practice:** After creating the class instance in your test, directly set the relevant attribute (e.g., `extractor.downloads_dir = temp_directory`) to point to a temporary directory provided by a test fixture.

- **Clean Up Before Each Test:**
  - Always remove any files in the temporary directory that could interfere with your test before running extraction or similar operations.

- **Avoid Global State:**
  - Do not rely on or modify global state (such as the real downloads directory) in your tests. Always use isolated, temporary directories.

- **Why Not Just Mock get_path?**
  - If you mock `get_path` after the class is instantiated, it will not affect the already-initialized instance. This is a common pitfall when using patching/mocking in Python tests.

#### Example: Correct Way to Patch for Extraction Tests

```python
extractor = ENEMExtractor()
extractor.downloads_dir = temp_directory  # temp_directory is a pytest fixture
# Now run your extraction logic and assertions
```

This approach ensures your tests are robust, isolated, and do not depend on or affect real files in your project.

## 🛠️ Development

### Development Setup

```bash
# Install development dependencies
make install-dev

# Setup pre-commit hooks
make pre-commit

# Format code
make format

# Lint code
make lint
```

### Available Commands

```bash
# See all available commands
make help

# Database operations
make test-db
make db-status

# Airflow operations
make airflow-up
make airflow-down
make airflow-logs

# Docker operations
make docker-compose-up
make docker-compose-down

# Cleanup
make clean
```

### Development Workflow

1. **Setup**: `make install-dev`
2. **Test**: `make test`
3. **Format**: `make format`
4. **Lint**: `make lint`
5. **Run**: `make airflow-up`

### Code Quality

The project includes:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pre-commit**: Git hooks

### Production Readiness and Future Improvements

#### Current Limitations

1. **Storage Strategy**: 
   - Currently uses Docker volumes for file storage
   - Not ideal for production with large datasets
   - Consider migrating to object storage (AWS S3, GCS, Azure Blob)

2. **Error Handling in Airflow**:
   - Current DAGs use try/catch blocks that may mask failures
   - Tasks can succeed even when operations fail
   - Need to implement proper error checking and DAG termination

#### Planned Improvements

1. **Object Storage Integration**:
   - Replace Docker volume storage with S3/GCS/Azure Blob
   - Implement proper file lifecycle management
   - Add cost optimization for storage

2. **Enhanced Error Handling**:
   - Add validation checks after each critical operation
   - Implement proper DAG failure propagation
   - Add retry mechanisms with exponential backoff
   - Ensure DAG stops when critical steps fail

3. **Monitoring and Alerting**:
   - Add comprehensive logging and monitoring
   - Implement alerting for pipeline failures
   - Add performance metrics and dashboards

## 📚 Documentation

### Main Documentation

- **README.md** - This file (project overview and quick start)
- **src/README.md** - Source code documentation and module guide
- **dags/README.md** - Airflow DAGs documentation and workflow guide

### Configuration Documentation

- **config/README.md** - Configuration management guide
- **config/config.yml** - Unified configuration file
- **config/env.template** - Environment variables template

### Testing Documentation

- **tests/README.md** - Comprehensive testing guide and test structure


- **scripts/README.md** - Utility scripts documentation

### Migration and History

- **TEST_CONSOLIDATION_SUMMARY.md** - Test consolidation details
- **TEST_DAG_REMOVAL_SUMMARY.md** - DAG removal and cleanup details

## 🤝 Contributing

### Development Guidelines

1. **Fork** the repository
2. **Create** a feature branch
3. **Follow** the coding standards (run `make format` and `make lint`)
4. **Add** tests for new functionality
5. **Update** documentation as needed
6. **Submit** a pull request

### Code Standards

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Ensure all tests pass
- Update documentation for new features

### Testing Requirements

- All new code must have corresponding tests
- Maintain test coverage above 80%
- Run full test suite before submitting PR
- Include integration tests for database operations

## 🆘 Support

### Common Issues

1. **Database Connection Issues**
   - Verify credentials in `config/.env`
   - Check database services are running
   - Test connections with `make test-db`

2. **Airflow Issues**
   - Check service logs: `make airflow-logs`
   - Verify database connectivity
   - Restart services: `make airflow-restart`

3. **Metabase Connection Issues**
   - Verify ETL database is running on port 5433
   - Check credentials in Metabase connection settings
   - Ensure database contains data (run ETL pipeline first)

4. **Configuration Issues**
   - Validate configuration: `python -c "from src.config import config_manager; print(config_manager.validate())"`
   - Check environment variables are set
   - Review `config/README.md` for setup instructions

5. **Windows Path Issues**
   - Move project to `C:\microdados` if experiencing path-related errors
   - Avoid spaces and special characters in project path
   - Use PowerShell or Command Prompt with administrator privileges

6. **Docker Compose File Permission Issues**
   - **Error**: `failed to solve: error from sender: open C:\microdados\logs\scheduler\latest: The file cannot be accessed by the system`
   - **Cause**: Windows file permission conflicts with Docker build context
   - **Solution**: 
     ```powershell
     # Stop all containers first
     docker-compose down
     
     # Clean up problematic log files
     Remove-Item -Recurse -Force logs\* -ErrorAction SilentlyContinue
     
     # Try running docker-compose again
     docker-compose up -d
     ```
   - **Prevention**: The `logs/` directory is gitignored and will be recreated automatically
   - **Alternative**: If the issue persists, restart Docker Desktop and try again

### Getting Help

- Check the documentation in the `docs/` directory

- Run tests to verify your setup: `make test`
- Check logs for detailed error messages

### Reporting Issues

When reporting issues, please include:

- Operating system and Python version
- Project path (especially important for Windows users)
- Configuration details (without sensitive data)
- Error messages and logs
- Steps to reproduce the issue
- Expected vs actual behavior

## 🧹 Cleanup and GitHub Readiness

This project has been cleaned of all unnecessary files before upload:
- All log files and directories (logs/, *.log) have been removed
- Python cache directories (__pycache__/ and .pytest_cache/) have been removed
- The virtual environment directory (venv/) has been removed
- No .env or sensitive files are present
- Data and downloads directories are empty or gitignored

The `.gitignore` is configured to prevent these files from being committed in the future.

You can safely upload this project to GitHub.