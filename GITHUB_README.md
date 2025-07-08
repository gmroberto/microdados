# ENEM Microdata ETL Pipeline

A comprehensive ETL pipeline for processing ENEM (Brazilian National High School Exam) microdata with Airflow integration, featuring a unified configuration system and robust data processing capabilities.

## 🚀 Quick Start

### Prerequisites
- **Docker and Docker Compose** (recommended)
- **Python 3.8+** (for local development)
- **PostgreSQL** (if not using Docker)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd microdados
```

### 2. Configure Environment
```bash
# Copy environment template
cp config/env.template config/.env

# Edit config/.env with your database credentials
# IMPORTANT: You must configure the .env file for the pipeline to work!
```

### 3. Start with Docker (Recommended)
```bash
# Start all services
docker-compose up -d

# Check services
docker-compose ps
```

### 4. Access Web Interfaces
- **Airflow Web UI**: http://localhost:8080 (username: `airflow`, password: `airflow`)
- **Metabase Dashboard**: http://localhost:3000

### 5. Run the Pipeline
1. Navigate to the DAGs tab in Airflow
2. Find `enem_etl_pipeline_advanced`
3. Click "Trigger DAG" to start the pipeline

## 📋 Project Status

### ✅ Ready for Production
- **Complete ETL Pipeline**: Download, extract, load, and process ENEM microdata
- **Triple Database Architecture**: Separate databases for Airflow, ETL data, and Metabase
- **United Table Logic**: Combines data from multiple years into a single optimized table
- **Comprehensive Testing**: Unit, integration, and end-to-end test suites
- **Docker Containerization**: Complete development environment
- **Metabase Integration**: Built-in business intelligence dashboard
- **Unified Configuration**: Single `config.yml` file with environment variable support

### 🔧 Key Features
- **Automated Data Pipeline**: Complete ETL process from download to database
- **Airflow Integration**: Production-ready DAGs for orchestration
- **Robust Error Handling**: Comprehensive error recovery and retry logic
- **Database Optimization**: Efficient data loading with chunked processing
- **Cross-Platform Support**: Works on Windows, Linux, and macOS
- **Progress Tracking**: Detailed logging and progress monitoring
- **File Cleanup**: Automated cleanup of temporary files

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
├── tests/                 # Comprehensive test suite

├── config/                # Unified configuration
│   ├── config.yml        # Single configuration file
│   ├── env.template      # Environment variables template
│   └── schemas/          # Database table schemas
├── docker-compose.yml    # Development environment
├── Dockerfile            # Containerization
└── Makefile              # Development tasks
```

## 🗄️ Database Architecture

This project uses **three separate PostgreSQL databases**:

1. **Airflow Database** (Port 5432): Stores Airflow metadata and DAG execution history
2. **ETL Database** (Port 5433): Stores processed ENEM microdata and analysis tables
3. **Metabase Database** (Port 5434): Stores Metabase dashboard configurations

## 🧪 Testing

### Quick Test (No Database Required)
```bash
# Run basic tests
python tests/run_tests.py

# Run with verbose output
python tests/run_tests.py --verbose

# Run with coverage
python tests/run_tests.py --coverage
```

### Comprehensive Testing
```bash
# Run all tests including database (if configured)
python tests/run_tests.py --database

# Run only database tests
python tests/run_tests.py --database-only
```

## 🔧 Development

### Available Commands
```bash
# See all available commands
make help

# Install dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Start Airflow
make airflow-up
```

## 📊 Data Processing

### Supported Years
The pipeline supports ENEM microdata from 1998 to 2023 (26 years of data).

### Data Flow
1. **Download**: Automated downloading from INEP's official website
2. **Extract**: ZIP file extraction and CSV processing
3. **Load**: Database loading with chunked processing
4. **Unite**: Creation of unified table combining multiple years
5. **Optimize**: Index creation for performance
6. **Analyze**: Metabase integration for data visualization

## 🛠️ Configuration

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
```

### Configuration Hierarchy
1. **Environment Variables** (`.env` file or system environment)
2. **Unified Configuration** (`config/config.yml` with variable substitution)
3. **Hardcoded defaults** (in `src/config.py`)

## 📚 Documentation

- **README.md** - This file (project overview and quick start)
- **src/README.md** - Source code documentation and module guide
- **dags/README.md** - Airflow DAGs documentation and workflow guide
- **config/README.md** - Configuration management guide
- **tests/README.md** - Comprehensive testing guide


## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Follow** the coding standards (run `make format` and `make lint`)
4. **Add** tests for new functionality
5. **Update** documentation as needed
6. **Submit** a pull request

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

3. **Configuration Issues**
   - Validate configuration: `python -c "from src.config import config_manager; print(config_manager.validate())"`
   - Check environment variables are set
   - Review `config/README.md` for setup instructions

### Getting Help

- Check the documentation in the project directories

- Run tests to verify your setup: `make test`
- Check logs for detailed error messages

## 🎯 Project Goals

This project aims to provide:
- **Easy Setup**: Simple configuration and Docker-based deployment
- **Scalability**: Handle large datasets efficiently
- **Reliability**: Robust error handling and recovery
- **Flexibility**: Support for different deployment scenarios
- **Analytics**: Built-in data visualization with Metabase
- **Maintainability**: Clean code structure and comprehensive testing

## 📈 Performance

- **Chunked Processing**: Handles large files efficiently
- **Database Optimization**: Proper indexing and query optimization
- **Memory Management**: Efficient memory usage for large datasets
- **Parallel Processing**: Support for concurrent operations

## 🔒 Security

- **Environment Variables**: Sensitive data stored in environment variables
- **Database Isolation**: Separate databases for different purposes
- **Access Control**: Proper database user permissions
- **No Hardcoded Secrets**: All sensitive data externalized

## 🧹 Cleanup and GitHub Readiness

- All log files and directories (logs/, *.log) have been removed
- Python cache directories (__pycache__/ and .pytest_cache/) have been removed
- The virtual environment directory (venv/) has been removed
- No .env or sensitive files are present
- Data and downloads directories are empty or gitignored

The `.gitignore` is configured to prevent these files from being committed in the future.

You can safely upload this project to GitHub.

---

**Ready for production use!** This project has been thoroughly tested and is ready for deployment in production environments. 