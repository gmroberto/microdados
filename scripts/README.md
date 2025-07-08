# Utility Scripts

This directory contains utility scripts for setting up, managing, and maintaining the ENEM Microdata ETL Pipeline. These scripts automate common tasks and provide development tools.

## 📁 Scripts Overview

- **`setup_env.py`** - Automated environment setup
- **`dev_setup.py`** - Development environment setup
- **`start_airflow.py`** - Airflow service management

## 🚀 Getting Started

### Prerequisites

Before running the scripts, ensure you have:

1. **Python Environment**: Python 3.8+ installed
2. **Project Structure**: All project files in place
3. **Dependencies**: Required packages installed

```bash
# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-test.txt
```

### Running Scripts

```bash
# Setup environment
python scripts/setup_env.py

# Setup development environment
python scripts/dev_setup.py

# Start Airflow
python scripts/start_airflow.py
```

## ⚙️ Environment Setup (`setup_env.py`)

### Purpose

Automates the creation and configuration of the `.env` file from the template, making it easier for new users to get started.

### Features

- **Template Copying**: Copies `env.template` to `.env`
- **Interactive Setup**: Guides users through configuration
- **Validation**: Checks for required environment variables
- **Backup**: Creates backup of existing `.env` files

### Usage

```bash
# Basic setup
python scripts/setup_env.py

# Interactive setup
python scripts/setup_env.py --interactive

# Force overwrite
python scripts/setup_env.py --force
```

### Example Output

```
🔧 ENEM Pipeline Environment Setup
=====================================

📋 Checking current environment...
✅ Project structure verified
✅ Template file found: config/env.template

📝 Creating .env file...
✅ Copied env.template to config/.env

⚠️  IMPORTANT: Please edit config/.env with your actual database credentials!

📋 Required environment variables:
- DB_PASSWORD: ETL database password
- AIRFLOW_DB_PASSWORD: Airflow database password
- METABASE_DB_PASSWORD: Metabase database password

✅ Environment setup completed!
```

### Configuration Options

The script supports several command-line options:

- `--interactive`: Run in interactive mode with prompts
- `--force`: Overwrite existing `.env` file
- `--backup`: Create backup of existing `.env` file
- `--validate`: Validate environment after setup

## 🛠️ Development Setup (`dev_setup.py`)

### Purpose

Sets up a complete development environment including virtual environment, dependencies, and development tools.

### Features

- **Virtual Environment**: Creates and activates virtual environment
- **Dependency Installation**: Installs all required packages
- **Development Tools**: Sets up pre-commit hooks and linting
- **Configuration**: Initializes development configuration

### Usage

```bash
# Complete development setup
python scripts/dev_setup.py

# Setup without virtual environment
python scripts/dev_setup.py --no-venv

# Install specific components
python scripts/dev_setup.py --deps --tools --config
```

### Example Output

```
🛠️  Development Environment Setup
=====================================

📦 Creating virtual environment...
✅ Virtual environment created: venv/

📚 Installing dependencies...
✅ Production dependencies installed
✅ Development dependencies installed

🔧 Setting up development tools...
✅ Pre-commit hooks installed
✅ Code formatting tools configured
✅ Linting tools configured

⚙️  Initializing configuration...
✅ Environment file created
✅ Configuration validated

🎉 Development environment setup completed!

📋 Next steps:
1. Activate virtual environment: source venv/bin/activate
2. Edit config/.env with your database credentials
3. Run tests: make test
4. Start development: make airflow-up
```

### Setup Components

1. **Virtual Environment**
   - Creates isolated Python environment
   - Installs dependencies in isolation
   - Provides consistent development environment

2. **Dependencies**
   - Production requirements (`requirements.txt`)
   - Development requirements (`requirements-test.txt`)
   - Optional development tools

3. **Development Tools**
   - Pre-commit hooks for code quality
   - Black for code formatting
   - isort for import sorting
   - flake8 for linting
   - mypy for type checking

4. **Configuration**
   - Environment file setup
   - Configuration validation
   - Development-specific settings

## 🚀 Airflow Management (`start_airflow.py`)

### Purpose

Manages Airflow services including startup, shutdown, and health monitoring.

### Features

- **Service Management**: Start/stop Airflow services
- **Health Monitoring**: Check service health
- **Log Management**: View and manage logs
- **Configuration**: Airflow-specific configuration

### Usage

```bash
# Start all Airflow services
python scripts/start_airflow.py

# Start specific services
python scripts/start_airflow.py --webserver --scheduler

# Check service health
python scripts/start_airflow.py --health

# View logs
python scripts/start_airflow.py --logs
```

### Example Output

```
🚀 Airflow Service Management
=====================================

📋 Starting Airflow services...
✅ PostgreSQL database started
✅ Airflow webserver started
✅ Airflow scheduler started

🔍 Checking service health...
✅ Database connection: OK
✅ Webserver: http://localhost:8080
✅ Scheduler: Running

📊 Service Status:
- PostgreSQL: Running (port 5432)
- Airflow Webserver: Running (port 8080)
- Airflow Scheduler: Running

🎉 All services started successfully!

📋 Access Airflow at: http://localhost:8080
Username: airflow
Password: airflow
```

### Service Management

1. **Database Services**
   - PostgreSQL for Airflow metadata
   - PostgreSQL for ETL data
   - PostgreSQL for Metabase

2. **Airflow Services**
   - Airflow webserver
   - Airflow scheduler
   - Airflow worker (if using Celery)

3. **Monitoring**
   - Service health checks
   - Log monitoring
   - Performance metrics

## 🔧 Script Development

### Script Structure

All scripts follow a consistent structure:

```python
#!/usr/bin/env python3
"""
Script description and purpose.

This script provides:
1. [First feature]
2. [Second feature]
3. [Third feature]
"""

import argparse
import sys
from pathlib import Path

def main():
    """Main script execution."""
    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument("--option", help="Option description")
    args = parser.parse_args()
    
    try:
        # Script logic here
        pass
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Best Practices

1. **Error Handling**: Always handle exceptions gracefully
2. **Logging**: Use appropriate logging levels
3. **Documentation**: Include comprehensive docstrings
4. **Validation**: Validate inputs and configurations
5. **Cleanup**: Clean up resources properly

### Adding New Scripts

When adding new scripts:

1. **Follow the Pattern**: Use the existing script structure
2. **Add Documentation**: Include comprehensive docstrings
3. **Add Arguments**: Use argparse for command-line options
4. **Add Tests**: Create corresponding test cases
5. **Update This README**: Document the new script

## 🧪 Testing Scripts

### Running Script Tests

```bash
# Test all scripts
python -m pytest tests/unit/test_scripts.py -v

# Test specific script
python -m pytest tests/unit/test_scripts.py::test_setup_env -v
```

### Script Validation

Scripts include built-in validation:

- Configuration validation
- Environment checks
- Dependency verification
- Error handling validation

## 📈 Performance Considerations

### Script Optimization

1. **Efficient I/O**: Use appropriate file handling methods
2. **Memory Management**: Handle large files efficiently
3. **Parallel Processing**: Use multiprocessing where appropriate
4. **Caching**: Cache expensive operations

### Monitoring

- Execution time tracking
- Resource usage monitoring
- Error rate tracking
- Performance metrics collection

## 🔒 Security Considerations

### Script Security

- Validate all inputs
- Sanitize file paths
- Use secure configuration methods
- Handle sensitive data appropriately

### Environment Security

- Secure credential management
- Environment variable protection
- File permission management
- Access control implementation

## 🚨 Troubleshooting

### Common Issues

1. **Permission Errors**
   - Check file permissions
   - Run with appropriate privileges
   - Verify directory access

2. **Configuration Errors**
   - Validate configuration files
   - Check environment variables
   - Verify file paths

3. **Dependency Issues**
   - Check Python version
   - Verify package installation
   - Update dependencies

4. **Service Issues**
   - Check service status
   - Verify port availability
   - Check log files

### Debugging Scripts

```bash
# Enable debug mode
python scripts/setup_env.py --debug

# Verbose output
python scripts/dev_setup.py --verbose

# Dry run mode
python scripts/start_airflow.py --dry-run
```

### Getting Help

```bash
# Show help for any script
python scripts/setup_env.py --help
python scripts/dev_setup.py --help
python scripts/start_airflow.py --help
```

## 📚 Related Documentation

- **Main README.md** - Project overview and setup
- **config/README.md** - Configuration management
- **tests/README.md** - Testing documentation
- **Makefile** - Development commands

## 🤝 Contributing Scripts

When contributing new scripts:

1. **Follow Standards**: Use the established script patterns
2. **Add Documentation**: Include comprehensive documentation
3. **Add Tests**: Create corresponding test cases
4. **Update README**: Document the new script here
5. **Handle Errors**: Implement proper error handling
6. **Validate Inputs**: Add input validation and sanitization

### Script Template

```python
#!/usr/bin/env python3
"""
[Script Name] - [Brief description]

This script provides:
1. [First feature]
2. [Second feature]
3. [Third feature]

Usage:
    python scripts/[script_name].py [options]

Examples:
    python scripts/[script_name].py --option value
    python scripts/[script_name].py --help
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def validate_environment() -> bool:
    """Validate the environment before running the script."""
    # Add validation logic here
    return True

def main() -> int:
    """Main script execution."""
    parser = argparse.ArgumentParser(description="[Script description]")
    parser.add_argument("--option", help="Option description")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Setup logging
    setup_logging("DEBUG" if args.verbose else "INFO")
    logger = logging.getLogger(__name__)
    
    try:
        # Validate environment
        if not validate_environment():
            logger.error("Environment validation failed")
            return 1
        
        # Script logic here
        logger.info("Script execution completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 