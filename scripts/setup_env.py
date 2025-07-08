#!/usr/bin/env python3
"""
Environment setup script for ENEM Microdata ETL Pipeline.
This script helps users create their .env file from the template.
"""

import os
import shutil
from pathlib import Path

def setup_environment():
    """Set up the environment by creating .env file from template."""
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    config_dir = project_root / "config"
    
    env_template = config_dir / "env.template"
    env_file = config_dir / ".env"
    
    print("🔧 ENEM Microdata ETL Pipeline - Environment Setup")
    print("=" * 50)
    
    # Check if .env already exists
    if env_file.exists():
        print(f"⚠️  .env file already exists at: {env_file}")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Copy template to .env
    try:
        shutil.copy2(env_template, env_file)
        print(f"✅ Created .env file at: {env_file}")
        print("\n📝 Next steps:")
        print("1. Edit the .env file and fill in your database credentials")
        print("2. Make sure your PostgreSQL database is running")
        print("3. Run the ETL pipeline")
        print(f"\n📁 .env file location: {env_file}")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        print(f"Please manually copy {env_template} to {env_file}")

if __name__ == "__main__":
    setup_environment() 