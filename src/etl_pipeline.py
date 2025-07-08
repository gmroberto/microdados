import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from config import get_path, get_setting
from downloader import ENEMDownloader
from extractor import ENEMExtractor
from loader import ENEMLoader

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_etl_pipeline(years: Optional[List[str]] = None, skip_download: bool = False) -> None:
    """
    Execute the complete ETL pipeline.
    
    Args:
        years: Optional list of years to process (e.g., ['2019', '2020'])
        skip_download: If True, skip the download phase
    """
    try:
        logger.info("=== Starting ETL Pipeline ===")
        
        # Download Phase
        if not skip_download:
            logger.info("1. Download Phase")
            try:
                downloader = ENEMDownloader()
                downloader.download_all(years)
                logger.info("Download phase completed successfully")
            except Exception as e:
                logger.error(f"Download phase failed: {e}")
                raise RuntimeError(f"Download phase failed: {e}") from e
        
        # Extract Phase
        logger.info("2. Extract Phase")
        try:
            extractor = ENEMExtractor()
            if not extractor.extract_all():
                logger.warning("Issues occurred during extraction")
            else:
                logger.info("Extract phase completed successfully")
        except Exception as e:
            logger.error(f"Extract phase failed: {e}")
            raise RuntimeError(f"Extract phase failed: {e}") from e
        
        # Load Phase
        logger.info("3. Load Phase")
        try:
            loader = ENEMLoader()
            loader.load_all_files(str(get_path('downloads')))
            logger.info("Load phase completed successfully")
        except Exception as e:
            logger.error(f"Load phase failed: {e}")
            raise RuntimeError(f"Load phase failed: {e}") from e
        
        # Create United Table
        logger.info("4. Create United Table")
        try:
            default_table = get_setting('united_table_name', 'enem_microdado_2011_2023')
            table_created = loader.create_united_table(default_table, drop_if_exists=False)
            if table_created:
                logger.info("United table creation completed successfully")
            else:
                logger.info("United table already exists, skipping creation")
        except Exception as e:
            logger.error(f"United table creation failed: {e}")
            raise RuntimeError(f"United table creation failed: {e}") from e
        
        # Populate United Table
        logger.info("5. Populate United Table")
        try:
            success = loader.populate_united_table(default_table)
            if success:
                logger.info("United table population completed successfully")
            else:
                logger.warning("United table population failed or was skipped")
        except Exception as e:
            logger.error(f"United table population failed: {e}")
            raise RuntimeError(f"United table population failed: {e}") from e
        
        # Create Indexes
        logger.info("6. Create Indexes")
        try:
            success = loader.create_indexes(default_table)
            if success:
                logger.info("Index creation completed successfully")
            else:
                logger.warning("Index creation failed or was skipped")
        except Exception as e:
            logger.error(f"Index creation failed: {e}")
            raise RuntimeError(f"Index creation failed: {e}") from e
        
        # Cleanup
        try:
            loader.close()
            logger.info("Database connections closed successfully")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
        
        logger.info("=== ETL Pipeline Completed Successfully ===")
        
    except Exception as e:
        logger.error(f"Error in ETL pipeline: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise


if __name__ == "__main__":
    # Run the complete pipeline
    logger.info("Starting ETL pipeline...")
    run_etl_pipeline()
    