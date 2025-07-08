#!/usr/bin/env python3
"""
Startup script for ENEM ETL Pipeline with Airflow.
This script helps users start the Airflow services and provides guidance.
"""

import sys
import subprocess
import time
import webbrowser
from pathlib import Path


def check_docker():
    """Check if Docker is available."""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Docker found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not found. Please install Docker Desktop or Docker Engine.")
        return False


def check_docker_compose():
    """Check if Docker Compose is available."""
    try:
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Docker Compose found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker Compose not found. Please install Docker Compose.")
        return False


def start_airflow():
    """Start Airflow services using Docker Compose."""
    print("\n🚀 Starting Airflow services...")
    
    try:
        # Start services in detached mode
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        print("✅ Airflow services started successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Airflow services: {e}")
        return False


def wait_for_airflow():
    """Wait for Airflow to be ready."""
    print("\n⏳ Waiting for Airflow to be ready...")
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            result = subprocess.run(['curl', '-f', 'http://localhost:8080/health'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Airflow is ready!")
                return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        attempt += 1
        print(f"   Attempt {attempt}/{max_attempts}...")
        time.sleep(10)
    
    print("⚠️  Airflow may still be starting up. Please check manually.")
    return False


def open_airflow_ui():
    """Open Airflow UI in the default browser."""
    try:
        webbrowser.open('http://localhost:8080')
        print("🌐 Opening Airflow UI in your browser...")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("   Please manually open: http://localhost:8080")


def print_instructions():
    """Print instructions for using the pipeline."""
    print("\n" + "="*60)
    print("🎉 ENEM ETL Pipeline - Airflow is Running!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Access Airflow Web UI at: http://localhost:8080")
    print("2. Default credentials: airflow / airflow")
    print("3. Navigate to DAGs tab")
    print("4. Find 'enem_etl_pipeline_advanced' DAG")
    print("5. Click 'Trigger DAG' to start the pipeline manually")
    print("\n⚙️  Configuration:")
    print("- Modify Airflow variables in Admin > Variables")
    print("- Key variables: enem_years, skip_download")
    print("\n🔧 Useful Commands:")
    print("- View logs: docker-compose logs -f")
    print("- Stop services: docker-compose down")
    print("- Restart services: docker-compose restart")
    print("- Rebuild and restart: docker-compose up --build -d")
    print("\n📁 Data Locations:")
    print("- Downloads: ./downloads/")
    print("- Database: PostgreSQL (enem_microdata)")
    print("- Main table: enem_united")
    print("\n💡 Note: Database initialization is now automatic!")
    print("="*60)


def main():
    """Main function."""
    print("🔧 ENEM ETL Pipeline - Airflow Startup")
    print("="*40)
    
    # Check prerequisites
    if not check_docker():
        sys.exit(1)
    
    if not check_docker_compose():
        sys.exit(1)
    
    # Start Airflow
    if not start_airflow():
        sys.exit(1)
    
    # Wait for Airflow to be ready
    wait_for_airflow()
    
    # Open UI
    open_airflow_ui()
    
    # Print instructions
    print_instructions()


if __name__ == "__main__":
    main() 