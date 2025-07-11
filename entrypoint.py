#!/usr/bin/env python3
"""
Simplified Airflow entrypoint script with basic database initialization
"""

import os
import sys
import time
import subprocess
import psycopg2
from psycopg2 import OperationalError


def wait_for_database():
    """Wait for PostgreSQL database to be ready."""
    print("Waiting for database to be ready...")
    
    # Get database connection details from environment or use defaults
    host = os.getenv('AIRFLOW__DATABASE__SQL_ALCHEMY_HOST', 'postgres')
    database = os.getenv('AIRFLOW__DATABASE__SQL_ALCHEMY_DATABASE', 'airflow')
    user = os.getenv('AIRFLOW__DATABASE__SQL_ALCHEMY_USER', 'enem_user')
    password = os.getenv('AIRFLOW__DATABASE__SQL_ALCHEMY_PASSWORD', 'enem_password')
    
    max_retries = 30
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )
            conn.close()
            print("Database is ready!")
            return True
        except OperationalError:
            print(f"Database not ready, waiting... (attempt {attempt + 1}/{max_retries})")
            time.sleep(2)
    
    print("Database failed to become ready")
    return False


def check_database_initialized():
    """Check if Airflow database is initialized."""
    print("Checking if Airflow database is initialized...")
    
    # Get database connection details from environment or use defaults
    host = os.getenv('AIRFLOW__DATABASE__SQL_ALCHEMY_HOST', 'postgres')
    database = os.getenv('AIRFLOW__DATABASE__SQL_ALCHEMY_DATABASE', 'airflow')
    user = os.getenv('AIRFLOW__DATABASE__SQL_ALCHEMY_USER', 'enem_user')
    password = os.getenv('AIRFLOW__DATABASE__SQL_ALCHEMY_PASSWORD', 'enem_password')
    
    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        # Check if the log table exists (this is created by airflow db init)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'log'
            );
        """)
        
        log_table_exists = cursor.fetchone()[0]
        
        # Also check if the slot_pool table exists (for pools)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'slot_pool'
            );
        """)
        
        pool_table_exists = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        if log_table_exists and pool_table_exists:
            print("Database already initialized with all required tables")
            return True
        else:
            print(f"Database not fully initialized - log table: {log_table_exists}, pool table: {pool_table_exists}")
            return False
            
    except Exception as e:
        print(f"Error checking database: {e}")
        return False


def initialize_database():
    """Initialize Airflow database using airflow db init."""
    print("Initializing Airflow database...")
    
    try:
        # Set environment variables for Airflow
        env = os.environ.copy()
        env['AIRFLOW__CORE__EXECUTOR'] = 'LocalExecutor'
        env['AIRFLOW__CORE__LOAD_EXAMPLES'] = 'false'
        
        result = subprocess.run(
            ["airflow", "db", "init"],
            check=True,
            capture_output=True,
            text=True,
            env=env
        )
        print("Database initialized successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to initialize database: {e}")
        print(f"Error output: {e.stderr}")
        return False


def create_admin_user():
    """Create admin user if it doesn't exist."""
    print("Creating admin user...")
    
    try:
        env = os.environ.copy()
        env['AIRFLOW__CORE__EXECUTOR'] = 'LocalExecutor'
        env['AIRFLOW__CORE__LOAD_EXAMPLES'] = 'false'
        
        subprocess.run([
            "airflow", "users", "create",
            "--username", "airflow",
            "--firstname", "Admin",
            "--lastname", "User",
            "--role", "Admin",
            "--email", "admin@example.com",
            "--password", "airflow"
        ], check=True, env=env)
        print("Admin user created successfully")
    except subprocess.CalledProcessError:
        print("Admin user already exists or creation failed")


def ensure_default_pool():
    """Ensure the default pool exists."""
    print("Ensuring default pool exists...")
    
    try:
        env = os.environ.copy()
        env['AIRFLOW__CORE__EXECUTOR'] = 'LocalExecutor'
        env['AIRFLOW__CORE__LOAD_EXAMPLES'] = 'false'
        
        # Try to create the default pool
        subprocess.run([
            "airflow", "pools", "set",
            "default_pool",
            "32",
            "Default pool for tasks"
        ], check=True, env=env)
        print("Default pool created/updated successfully")
    except subprocess.CalledProcessError:
        print("Default pool already exists or creation failed")


def main():
    """Main function."""
    # Wait for database to be ready
    if not wait_for_database():
        sys.exit(1)
    
    # Check and initialize database if needed
    if not check_database_initialized():
        if not initialize_database():
            sys.exit(1)
    
    # Create admin user
    create_admin_user()
    
    # Ensure default pool exists
    ensure_default_pool()
    
    # Execute the main command
    if len(sys.argv) > 1:
        arguments = sys.argv[1:]
        airflow_command = ["airflow"] + arguments
        os.execvp("airflow", airflow_command)
    else:
        print("No command specified")


if __name__ == "__main__":
    main() 