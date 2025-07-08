# Configuration Management

This directory contains all configuration files for the ENEM Microdata ETL Pipeline. The project uses a unified configuration system with a single `config.yml` file and environment variable support.

## 📁 Files Overview

- **`config.yml`** - Unified configuration file with environment variable support
- **`env.template`** - Template for environment variables (copy to `.env`)
- **`airflow_init.py`** - Airflow initialization script
- **`download_history.json`** - Tracks downloaded files and their metadata
- **`defaulted_columns.json`** - Default column mappings for data processing
- **`schemas/`** - Database schema definitions
  - **`enem_tables.yml`** - Table schemas for ENEM microdata

## ⚙️ Configuration System

### Unified Configuration (`config.yml`)

The `config.yml` file serves as the single source of truth for all configuration settings. It supports environment variable substitution using the `${VAR:-default}` syntax.

#### Key Sections:

1. **Environment Settings**
   - `environment`: Current environment (development, staging, production)

2. **Application Settings**
   - `chunk_size`: Number of records to process in batches
   - `united_table_name`: Name of the combined data table
   - `log_level`: Logging verbosity
   - `skip_download`: Whether to skip file downloads
   - `enem_base_url`: Base URL for ENEM data downloads

3. **Airflow Configuration**
   - `enem_years`: List of years to process
   - `webserver_secret_key`: Secret key for Airflow web server
   - `load_examples`: Whether to load Airflow examples
   - `task_timeout`: Maximum task execution time
   - `executor`: Airflow executor type

4. **Metabase Configuration**
   - `port`: Metabase web server port
   - `host`: Metabase host address
   - Database connection settings
   - Security and performance settings

5. **Database Configuration**
   - **ETL Database**: Stores processed ENEM microdata
   - **Airflow Database**: Stores Airflow metadata
   - **Metabase Database**: Stores Metabase metadata

6. **File Paths and Patterns**
   - Directory paths for downloads, data, logs
   - File patterns for CSV and ZIP files

7. **Logging Configuration**
   - Log format and rotation settings

8. **Validation Settings**
   - Data validation rules and thresholds

### Environment Variables (`.env`)

Create a `.env` file from `env.template` with your actual database credentials:

```env
# ETL Database (for storing ENEM microdata)
DB_HOST=localhost
DB_PORT=5433
DB_NAME=enem_data
DB_USER=enem_etl_user
DB_PASSWORD=your_etl_password_here

# Airflow Database (for Airflow metadata)
AIRFLOW_DB_HOST=localhost
AIRFLOW_DB_PORT=5432
AIRFLOW_DB_NAME=airflow
AIRFLOW_DB_USER=enem_user
AIRFLOW_DB_PASSWORD=your_airflow_password_here

# Metabase Database (for Metabase metadata)
METABASE_DB_HOST=localhost
METABASE_DB_PORT=5434
METABASE_DB_NAME=metabase
METABASE_DB_USER=metabase_user
METABASE_DB_PASSWORD=your_metabase_password_here

# Optional: Secret keys
AIRFLOW__WEBSERVER__SECRET_KEY=your-secret-key-here
METABASE_ENCRYPTION_SECRET_KEY=your-metabase-secret-key-here
```

## 🔧 Configuration Usage

### In Python Code

```python
from src.config import config_manager

# Get configuration values
chunk_size = config_manager.get('application.chunk_size', 10000)
db_config = config_manager.get_database_config('etl')

# Validate configuration
if config_manager.validate():
    print("✅ Configuration is valid")

# Reload configuration
config_manager.reload()
```

### Environment Variable Substitution

The configuration system supports environment variable substitution:

```yaml
# In config.yml
database:
  etl:
    host: ${DB_HOST:-localhost}
    port: ${DB_PORT:-5433}
    password: ${DB_PASSWORD}  # No default - must be set
```

### Configuration Hierarchy

Configuration is loaded in this priority order:

1. **Environment Variables** (`.env` file or system environment)
2. **Unified Configuration** (`config.yml` with variable substitution)
3. **Hardcoded defaults** (in `src/config.py`)

## 🗄️ Database Configuration

### Triple Database Architecture

The project uses three separate PostgreSQL databases:

1. **ETL Database (Port 5433)**
   - **Purpose**: Stores processed ENEM microdata
   - **Database**: `enem_data`
   - **User**: `enem_etl_user`

2. **Airflow Database (Port 5432)**
   - **Purpose**: Stores Airflow metadata and DAG execution history
   - **Database**: `airflow`
   - **User**: `enem_user`

3. **Metabase Database (Port 5434)**
   - **Purpose**: Stores Metabase metadata and dashboard configurations
   - **Database**: `metabase`
   - **User**: `metabase_user`

### Database Connection Testing

Test database connections using:

```bash
# Test all database connections
make test-db

# Or run directly
python -m pytest tests/integration/test_databases.py -v
```

## 📊 Schema Management

### Table Schemas (`schemas/enem_tables.yml`)

The `schemas/enem_tables.yml` file defines the structure of ENEM microdata tables:

- Column definitions with data types
- Index specifications for performance
- Table relationships and constraints

### Schema Usage

```python
from src.config import config_manager

# Get schema path
schema_path = config_manager.get_schema_path()

# Load schema
with open(schema_path, 'r') as f:
    schema = yaml.safe_load(f)
```

## 🔄 Configuration Updates

### Adding New Settings

1. Add the setting to `config.yml` with appropriate defaults
2. Update `src/config.py` if needed for validation
3. Document the new setting in this README
4. Update tests if necessary

### Environment-Specific Configuration

For different environments, you can:

1. Use environment variables to override settings
2. Create environment-specific `.env` files
3. Use the `ENVIRONMENT` variable to load different configs

## 🧪 Configuration Testing

### Validation

```python
# Validate configuration
if config_manager.validate():
    print("✅ Configuration is valid")
else:
    print("❌ Configuration validation failed")
```

### Testing Configuration Loading

```python
# Test configuration loading
try:
    config = config_manager.get_config()
    print("✅ Configuration loaded successfully")
except Exception as e:
    print(f"❌ Configuration loading failed: {e}")
```

## 🔒 Security Considerations

### Sensitive Data

- Never commit `.env` files to version control
- Use strong passwords for database connections
- Generate secure secret keys for production
- Use environment variables for sensitive configuration

### Production Configuration

For production deployments:

1. Use strong, unique passwords
2. Generate secure secret keys
3. Use external secret management systems
4. Enable SSL/TLS for database connections
5. Restrict database access to necessary IPs

## 🚨 Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   - Ensure `.env` file exists and contains required variables
   - Check variable names match those in `config.yml`

2. **Database Connection Issues**
   - Verify database services are running
   - Check credentials in `.env` file
   - Test connections manually

3. **Configuration Loading Errors**
   - Check `config.yml` syntax
   - Verify file paths are correct
   - Ensure environment variables are set

4. **Schema Loading Issues**
   - Verify `schemas/enem_tables.yml` exists
   - Check YAML syntax in schema file
   - Ensure schema file is readable

### Debugging Configuration

```python
# Print complete configuration
print(config_manager.get_config())

# Print specific section
print(config_manager.get('database'))

# Check environment variables
import os
print(os.getenv('DB_PASSWORD'))
```

## 📚 Related Documentation

- **Main README.md** - Project overview and setup
- **src/config.py** - Configuration management implementation
- **docker-compose.yml** - Docker environment configuration
- **tests/unit/test_assertions.py** - Configuration testing 