"""
Pytest configuration for ENEM Microdata ETL Pipeline tests.
"""

import pytest
from pathlib import Path


def pytest_ignore_collect(collection_path):
    """Ignore collection of certain directories and files."""
    # Convert to Path object if it's a string
    path = Path(collection_path)
    
    # Ignore logs directory and its contents
    if 'logs' in path.parts:
        return True
    
    # Ignore downloads directory and its contents
    if 'downloads' in path.parts:
        return True
    
    # Ignore data directory and its contents
    if 'data' in path.parts:
        return True
    
    # Ignore virtual environment directories
    if any(venv_dir in path.parts for venv_dir in ['venv', 'env', '.venv']):
        return True
    
    # Ignore cache directories
    if any(cache_dir in path.parts for cache_dir in ['__pycache__', '.pytest_cache']):
        return True
    
    return False


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "test_mode": True,
        "database_required": False
    } 