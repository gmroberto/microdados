#!/usr/bin/env python3
"""
Airflow entrypoint script with automatic database initialization
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
    
    while True:
        try:
            conn = psycopg2.connect(
                host="postgres",
                database="airflow",
                user="enem_user",
                password="enem_password"
            )
            conn.close()
            print("Database is ready!")
            break
        except OperationalError:
            print("Database not ready, waiting...")
            time.sleep(2)


def check_database_initialized():
    """Check if Airflow database is initialized."""
    print("Checking if Airflow database is initialized...")
    
    try:
        # Try to connect and check if tables exist
        conn = psycopg2.connect(
            host="postgres",
            database="airflow",
            user="enem_user",
            password="enem_password"
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
        
        table_exists = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        if table_exists:
            print("Database already initialized")
            return True
        else:
            print("Database not initialized")
            return False
            
    except Exception as e:
        print(f"Error checking database: {e}")
        return False


def initialize_database():
    """Initialize Airflow database using airflow db init."""
    print("Initializing Airflow database...")
    
    try:
        # Use airflow db init command
        result = subprocess.run(
            ["airflow", "db", "init"],
            check=True,
            capture_output=True,
            text=True
        )
        print("Database initialized successfully")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to initialize database: {e}")
        print(f"Error output: {e.stderr}")
        return False


def create_admin_user():
    """Create admin user if it doesn't exist."""
    print("Creating admin user...")
    
    try:
        subprocess.run([
            "airflow", "users", "create",
            "--username", "airflow",
            "--firstname", "Admin",
            "--lastname", "User",
            "--role", "Admin",
            "--email", "admin@example.com",
            "--password", "airflow"
        ], check=True)
        print("Admin user created successfully")
    except subprocess.CalledProcessError:
        print("Admin user already exists or creation failed")


def main():
    """Main function."""
    # Wait for database
    wait_for_database()
    
    # Check and initialize database if needed
    if not check_database_initialized():
        if not initialize_database():
            sys.exit(1)
    
    # Create admin user
    create_admin_user()
    
    # Execute the main command
    if len(sys.argv) > 1:
        # Get all arguments after the script name
        # Example: if docker-compose runs "python entrypoint.py webserver"
        # then sys.argv = ["entrypoint.py", "webserver"] 
        # and arguments = ["webserver"]
        arguments = sys.argv[1:]
        
        # Always prepend "airflow" to make it an airflow command
        # Example: ["webserver"] becomes ["airflow", "webserver"]
        # Example: ["scheduler"] becomes ["airflow", "scheduler"]
        airflow_command = ["airflow"] + arguments
        
        # Execute the airflow command
        # This replaces the current process with the airflow command
        # Examples of what actually gets executed:
        # - os.execvp("airflow", ["airflow", "webserver"])  # starts the web interface
        # - os.execvp("airflow", ["airflow", "scheduler"])  # starts the task scheduler
        os.execvp("airflow", airflow_command)
    else:
        print("No command specified")


if __name__ == "__main__":
    main() 