"""
ETL Functions for ENEM Pipeline.
This module contains the core business logic functions used by the ENEM ETL pipeline.
These functions are pure and don't depend on Airflow context.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, Callable

from config import config_manager
from downloader import ENEMDownloader
from extractor import ENEMExtractor
from loader import ENEMLoader
from cleanup import CleanupManager

# Get configuration values from config manager
DOWNLOADS_DIR = Path(config_manager.get('paths.downloads'))
UNITED_TABLE_NAME = config_manager.get('application.united_table_name', 'enem_microdado_2011_2023')

# Configure logging
logger = logging.getLogger(__name__)


def _execute_with_logging(phase_name: str, func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """
    Generic wrapper that handles common logging and error handling patterns.
    
    Args:
        phase_name: Name of the phase for logging
        func: Function to execute
        *args, **kwargs: Arguments to pass to the function
    
    Returns:
        Dict containing status and any error information
    """
    try:
        logger.info(f"=== Starting {phase_name.replace('_', ' ').title()} Phase ===")
        
        result = func(*args, **kwargs)
        
        logger.info(f"=== {phase_name.replace('_', ' ').title()} Phase Completed ===")
        return {'status': 'success', 'error': None}
        
    except Exception as e:
        logger.error(f"{phase_name.replace('_', ' ').title()} phase failed: {str(e)}")
        return {'status': 'failed', 'error': str(e)}


def download_enem_data(years: Optional[list] = None, skip_download: bool = False) -> Dict[str, Any]:
    """
    Download ENEM microdata files.
    
    Args:
        years: List of years to download. If None, uses default configuration.
        skip_download: Whether to skip the download phase.
    
    Returns:
        Dict containing status and any error information.
    """
    if skip_download:
        logger.info("Skipping download phase as configured")
        return {'status': 'skipped', 'error': None}
    
    return _execute_with_logging('download', lambda: ENEMDownloader().download_all(years))


def extract_zip_files() -> Dict[str, Any]:
    """
    Extract ZIP files to CSV without deleting them.
    
    Returns:
        Dict containing status and any error information.
    """
    def _extract():
        extractor = ENEMExtractor()
        success = extractor.extract_all()
        if not success:
            logger.warning("Issues occurred during extraction")
            return {'status': 'warning', 'error': None}
        return {'status': 'success', 'error': None}
    
    return _execute_with_logging('extract', _extract)


def delete_zip_files() -> Dict[str, Any]:
    """
    Delete ZIP files after successful extraction.
    
    Returns:
        Dict containing status and any error information.
    """
    def _delete_zip():
        extractor = ENEMExtractor()
        success = extractor.delete_zip_files()
        if not success:
            logger.warning("Issues occurred during ZIP deletion")
            return {'status': 'warning', 'error': None}
        return {'status': 'success', 'error': None}
    
    return _execute_with_logging('delete_zip', _delete_zip)


def load_csv_files() -> Dict[str, Any]:
    """
    Load CSV files into database.
    
    Returns:
        Dict containing status and any error information.
    """
    def _load():
        loader = ENEMLoader()
        loader.load_all_files(str(DOWNLOADS_DIR))
        loader.close()
    
    return _execute_with_logging('load', _load)


def create_united_table_structure() -> Dict[str, Any]:
    """
    Create the unified table structure.
    
    Returns:
        Dict containing status and any error information.
    """
    def _create_table():
        loader = ENEMLoader()
        loader.create_united_table(UNITED_TABLE_NAME, drop_if_exists=True)
        loader.close()
    
    return _execute_with_logging('create_united_table', _create_table)


def populate_united_table_data() -> Dict[str, Any]:
    """
    Fill the unified table with data.
    
    Returns:
        Dict containing status and any error information.
    """
    def _populate():
        loader = ENEMLoader()
        loader.populate_united_table(UNITED_TABLE_NAME)
        loader.close()
    
    return _execute_with_logging('populate_united_table', _populate)


def create_database_indexes() -> Dict[str, Any]:
    """
    Create database indexes for performance.
    
    Returns:
        Dict containing status and any error information.
    """
    def _create_indexes():
        loader = ENEMLoader()
        loader.create_indexes(UNITED_TABLE_NAME)
        loader.close()
    
    return _execute_with_logging('create_indexes', _create_indexes)


def cleanup_csv_files() -> Dict[str, Any]:
    """
    Clean up CSV files from the downloads directory.
    
    Returns:
        Dict containing status and cleanup results.
    """
    try:
        logger.info("=== Starting CSV Cleanup Phase ===")
        
        cleanup_manager = CleanupManager()
        result = cleanup_manager.cleanup_csv_files()
        
        # Convert the detailed result to a simpler format for consistency
        if result['status'] == 'success':
            logger.info(f"CSV cleanup completed successfully. Deleted {result['files_deleted']} files.")
            return {'status': 'success', 'error': None, 'details': result}
        elif result['status'] == 'no_files':
            logger.info("No CSV files found to clean up")
            return {'status': 'success', 'error': None, 'details': result}
        elif result['status'] == 'partial':
            logger.warning(f"CSV cleanup partially completed. {result['files_deleted']} files deleted, {len(result['failed_deletions'])} failed.")
            return {'status': 'warning', 'error': None, 'details': result}
        else:
            logger.error(f"CSV cleanup failed: {result['error_message']}")
            return {'status': 'failed', 'error': result['error_message'], 'details': result}
        
    except Exception as e:
        logger.error(f"CSV cleanup phase failed: {str(e)}")
        return {'status': 'failed', 'error': str(e)}


def generate_pipeline_summary(statuses: Dict[str, str]) -> Dict[str, Any]:
    """
    Generate a summary of the pipeline execution.
    
    Args:
        statuses: Dictionary containing status of each phase.
    
    Returns:
        Dict containing summary information and any failed phases.
    """
    logger.info("=== Pipeline Execution Summary ===")
    
    for phase, status in statuses.items():
        logger.info(f"{phase.capitalize()} Phase: {status}")
    
    # Check if any phase failed
    failed_phases = [phase for phase, status in statuses.items() if status == 'failed']
    if failed_phases:
        logger.warning(f"Failed phases: {', '.join(failed_phases)}")
    
    logger.info("=== Pipeline Summary Completed ===")
    
    return {
        'statuses': statuses,
        'failed_phases': failed_phases,
        'overall_status': 'failed' if failed_phases else 'success'
    } 