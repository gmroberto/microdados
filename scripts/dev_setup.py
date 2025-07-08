#!/usr/bin/env python3
"""
Cross-platform development setup script for ENEM Microdata ETL project.
This script helps set up the development environment on both Windows and Linux.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def check_docker():
    """Check if Docker is available."""
    print("🔄 Checking Docker availability...")
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True, shell=False)
        if result.returncode == 0:
            print(f"✅ Docker is available: {result.stdout.strip()}")
            return True
        else:
            print("⚠️  Docker is not available. Please install Docker Desktop.")
            return False
    except FileNotFoundError:
        print("⚠️  Docker is not available. Please install Docker Desktop.")
        return False


def setup_virtual_environment():
    """Set up virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")


def install_dependencies():
    """Install project dependencies."""
    # Determine the correct activation command based on OS
    if platform.system() == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install production dependencies
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing production dependencies"):
        return False
    
    # Install development dependencies
    if not run_command(f"{pip_cmd} install -r requirements-test.txt", "Installing development dependencies"):
        return False
    
    return True


def create_directories():
    """Create necessary directories."""
    directories = [
        "data/raw",
        "data/processed", 
        "downloads",
        "logs",
        "plugins"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def setup_airflow():
    """Set up Airflow configuration."""
    # Create Airflow config directory if it doesn't exist
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Create subdirectories for new configuration structure
    (config_dir / "schemas").mkdir(exist_ok=True)
    (config_dir / "environments").mkdir(exist_ok=True)
    
    # Check if environment template exists
    env_example = config_dir / "env.example"
    if not env_example.exists():
        print("⚠️  Environment template not found. Please check config/.env.example")
    else:
        print("✅ Environment template found")
    
    # Check if database configuration exists
    db_config = config_dir / "database.yml"
    if not db_config.exists():
        print("⚠️  Database configuration not found. Please check config/database.yml")
    else:
        print("✅ Database configuration found")
    
    print("✅ Configuration setup completed")


def main():
    """Main setup function."""
    print("🚀 ENEM Microdata ETL - Development Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_docker():
        print("⚠️  Docker is recommended but not required for local development")
    
    # Setup steps
    steps = [
        ("Creating virtual environment", setup_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Creating directories", create_directories),
        ("Setting up Airflow", setup_airflow),
    ]
    
    for description, step_func in steps:
        if not step_func():
            print(f"❌ Setup failed at: {description}")
            sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Configure your environment:")
    print("   cp config/.env.example config/.env")
    print("   # Edit config/.env with your database credentials")
    print("3. Run tests: python tests/run_tests.py")
    print("4. Start Airflow: docker-compose up -d")
    print("5. Access Airflow UI: http://localhost:8080")


if __name__ == "__main__":
    main() 