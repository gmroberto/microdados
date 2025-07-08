#!/usr/bin/env python3
"""
Simple Airflow initialization for ENEM ETL Pipeline.
Sets up essential Airflow variables from configuration.
"""

import sys
import logging
from pathlib import Path

# Add project root to path for absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from config to avoid confusion with the config directory
from config import config_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_airflow_variables():
    """Set up Airflow variables from configuration."""
    try:
        from airflow.models import Variable
        
        config = config_manager.get_config()
        
        # Essential variables for the pipeline
        variables = {
            "enem_years": config.get('airflow', {}).get('enem_years', [2022, 2023]),
            "skip_download": config.get('application', {}).get('skip_download', False),
            "downloads_dir": config.get('paths', {}).get('downloads', 'downloads'),
            "united_table_name": config.get('application', {}).get('united_table_name', 'enem_microdado_2011_2023'),
            "chunk_size": config.get('application', {}).get('chunk_size', 10000),
            "log_level": config.get('application', {}).get('log_level', 'INFO'),
        }
        
        # Set variables in Airflow
        for key, value in variables.items():
            Variable.set(key, value, serialize_json=True)
            logger.info(f"✅ Set: {key} = {value}")
        
        logger.info("🎉 Airflow variables initialized!")
        return True
        
    except ImportError:
        logger.error("❌ Airflow not available. Run this in Airflow environment.")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    logger.info("🔧 Setting up Airflow variables...")
    success = setup_airflow_variables()
    
    if success:
        print("\n📋 Next steps:")
        print("1. Access Airflow UI: http://localhost:8080")
        print("2. Find 'enem_etl_dag' and trigger it")
        print("3. Check variables in Admin > Variables")
    else:
        sys.exit(1) 