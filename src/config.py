"""
Configuration management for ENEM Microdata ETL Pipeline.
Provides a centralized way to manage configuration across different environments.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any 
from dotenv import load_dotenv


class ConfigManager:
    """
    Centralized configuration manager that loads configuration from a unified YAML file
    with environment variable support.
    
    Configuration is loaded from:
    1. Unified config.yml file (with environment variable substitution)
    2. Environment variables (.env file)
    
    This provides a clean, single-source-of-truth approach to configuration management.
    """
    
    def __init__(self, environment: str = None):
        """
        Initialize configuration manager.
        
        Args:
            environment: Environment name (development, staging, production)
                        If None, will use ENVIRONMENT env var or default to 'development'
        """
        self.root_dir = Path(__file__).parent.parent
        self.config_dir = self.root_dir / "config"
        self.environment = environment or os.getenv('ENVIRONMENT', 'development')
        
        # Load environment variables first
        self._load_env_vars()
        
        # Load unified configuration
        self.config = self._load_config()
    
    def _load_env_vars(self):
        """Load environment variables from .env file."""
        env_file = self.config_dir / ".env"
        if env_file.exists():
            # Load with explicit encoding
            load_dotenv(env_file, encoding='utf-8')
        else:
            # Try to load from env.simple if .env doesn't exist
            simple_file = self.config_dir / "env.simple"
            if simple_file.exists():
                print(f"⚠️  No .env file found. Please copy {simple_file} to .env and configure your settings.")
            else:
                print("⚠️  No .env file found. Please create one with your database credentials.")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from unified config.yml file with environment variable substitution.
        """
        config_file = self.config_dir / "config.yml"
        if not config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_file}\n"
                f"Please ensure the config.yml file exists in the config directory."
            )
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        
        # Resolve relative paths to absolute paths
        if 'paths' in config:
            for key, path in config['paths'].items():
                if isinstance(path, str) and not Path(path).is_absolute():
                    config['paths'][key] = str(self.root_dir / path)
        
        # Apply environment variable replacement to the configuration
        return self._replace_env_placeholders(config)
    
    def _replace_env_placeholders(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Replace ${VAR:-default} placeholders with actual values."""
        if isinstance(config, dict):
            return {k: self._replace_env_placeholders(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_placeholders(v) for v in config]
        elif isinstance(config, str):
            if config.startswith('${') and config.endswith('}'):
                var_part = config[2:-1]  # Remove ${ and }
                if ':-' in var_part:
                    # Format: ${VAR:-default}
                    var_name, default = var_part.split(':-', 1)
                    return os.getenv(var_name, default)
                else:
                    # Format: ${VAR} (no default)
                    return os.getenv(var_part, '')
            else:
                # Not a placeholder, return as-is
                return config
        else:
            # Not a string, return as-is
            return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'database.etl.host')."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_database_config(self, db_type: str = 'etl') -> Dict[str, Any]:
        """Get database configuration for specified type."""
        db_config = self.config.get('database', {})
        if db_type == 'etl':
            return db_config.get('etl', {})
        elif db_type == 'airflow':
            return db_config.get('airflow', {})
        else:
            raise ValueError(f"Unknown database type: {db_type}")
    
    def get_schema_path(self) -> Path:
        """Get path to table schemas file."""
        return self.config_dir / "schemas" / "enem_tables.yml"
    
    def validate(self) -> bool:
        """Validate that all required configuration is present."""
        required_vars = [
            'DB_USER', 'DB_PASSWORD',
            'AIRFLOW_DB_USER', 'AIRFLOW_DB_PASSWORD'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            print("Please check your .env file or environment variables.")
            return False
        
        return True
    
    def reload(self):
        """Reload configuration from all sources."""
        self._load_env_vars()
        self.config = self._load_config()
        print("✅ Configuration reloaded successfully")
    
    def get_config(self) -> Dict[str, Any]:
        """Get the complete configuration dictionary."""
        return self.config.copy()
    
    def apply_env_replacements(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable replacement to any configuration dictionary."""
        return self._replace_env_placeholders(config)


# Global configuration instance
config_manager = ConfigManager()

# Convenience functions for common configuration access
def get_path(path_key: str) -> Path:
    """Get a path from configuration."""
    path_str = config_manager.get(f'paths.{path_key}')
    if not path_str:
        raise ValueError(f"Path '{path_key}' not found in configuration")
    return Path(path_str)

def get_setting(setting_key: str, default: Any = None) -> Any:
    """Get an application setting from configuration."""
    return config_manager.get(f'application.{setting_key}', default)

def get_url(url_key: str) -> str:
    """Get a URL from configuration."""
    # First try application section (where enem_base_url is defined)
    url = config_manager.get(f'application.{url_key}')
    if not url:
        # Fallback to urls section if it exists
        url = config_manager.get(f'urls.{url_key}')
    if not url:
        raise ValueError(f"URL '{url_key}' not found in configuration")
    return url

def get_pattern(pattern_key: str) -> str:
    """Get a file pattern from configuration."""
    pattern = config_manager.get(f'file_patterns.{pattern_key}')
    if not pattern:
        raise ValueError(f"Pattern '{pattern_key}' not found in configuration")
    return pattern

# Note: Use config_manager.get_database_config() directly instead of these convenience functions

def get_project_root() -> Path:
    """Get the project root directory path."""
    return Path(__file__).parent.parent
