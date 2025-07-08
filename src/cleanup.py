"""
Cleanup module for managing file cleanup operations.
Handles deletion of temporary files like CSV files from downloads folder.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from config import get_path

# Set up logging
logger = logging.getLogger(__name__)


class CleanupManager:
    """
    Manages cleanup operations for temporary files in the project.
    """
    
    def __init__(self, downloads_dir: Optional[Path] = None):
        """
        Initialize the cleanup manager.
        
        Args:
            downloads_dir: Path to downloads directory. If None, uses config default.
        """
        self.downloads_dir = downloads_dir or Path(get_path('downloads'))
        logger.info(f"CleanupManager initialized with downloads directory: {self.downloads_dir}")
    
    def _cleanup_files_by_extension(self, extension: str) -> Dict[str, any]:
        """
        Generic file cleanup function for any file extension.
        
        Args:
            extension: File extension to clean up (e.g., '.csv', '.zip')
        
        Returns:
            Dictionary containing cleanup results
        """
        result = {
            'status': 'unknown',
            'files_deleted': 0,
            'total_files': 0,
            'space_freed_bytes': 0,
            'failed_deletions': [],
            'error_message': None
        }
        
        try:
            logger.info(f"=== Starting {extension.upper()} Cleanup ===")
            
            # Ensure downloads directory exists
            if not self.downloads_dir.exists():
                logger.warning(f"Downloads directory {self.downloads_dir} does not exist")
                result['status'] = 'skipped'
                return result
            
            # Find all files with the specified extension
            pattern = f'**/*{extension}'
            files = list(self.downloads_dir.glob(pattern))
            
            if not files:
                logger.info(f"No {extension.upper()} files found in downloads directory")
                result['status'] = 'no_files'
                return result
            
            logger.info(f"Found {len(files)} {extension.upper()} files to delete")
            result['total_files'] = len(files)
            
            # Calculate total size before deletion
            total_size_before = sum(f.stat().st_size for f in files)
            
            # Delete each file
            deleted_count = 0
            failed_deletions = []
            
            for file_path in files:
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted: {file_path.name} ({file_size} bytes)")
                except Exception as e:
                    error_msg = f"Failed to delete {file_path.name}: {str(e)}"
                    logger.error(error_msg)
                    failed_deletions.append({
                        'file': str(file_path),
                        'error': str(e)
                    })
            
            # Calculate space freed
            space_freed = total_size_before
            logger.info(f"Successfully deleted {deleted_count} out of {len(files)} {extension.upper()} files")
            logger.info(f"Total space freed: {space_freed} bytes ({space_freed / (1024**3):.2f} GB)")
            
            # Set result status
            if failed_deletions:
                logger.warning(f"Failed to delete {len(failed_deletions)} files")
                result['status'] = 'partial'
            else:
                result['status'] = 'success'
            
            result['files_deleted'] = deleted_count
            result['space_freed_bytes'] = space_freed
            result['failed_deletions'] = failed_deletions
            
            logger.info(f"=== {extension.upper()} Cleanup Completed ===")
            
        except Exception as e:
            error_msg = f"{extension.upper()} cleanup failed: {str(e)}"
            logger.error(error_msg)
            result['status'] = 'failed'
            result['error_message'] = str(e)
        
        return result
    
    def cleanup_csv_files(self) -> Dict[str, any]:
        """
        Delete all CSV files from the downloads directory.
        
        Returns:
            Dictionary containing cleanup results
        """
        return self._cleanup_files_by_extension('.csv')
    
    def cleanup_zip_files(self) -> Dict[str, any]:
        """
        Delete all ZIP files from the downloads directory.
        
        Returns:
            Dictionary containing cleanup results
        """
        return self._cleanup_files_by_extension('.zip')
    
    def cleanup_all_temp_files(self) -> Dict[str, any]:
        """
        Clean up all temporary files (CSV and ZIP) from the downloads directory.
        
        Returns:
            Dictionary containing combined cleanup results
        """
        logger.info("=== Starting Complete Cleanup ===")
        
        csv_result = self.cleanup_csv_files()
        zip_result = self.cleanup_zip_files()
        
        # Combine results
        combined_result = {
            'status': 'unknown',
            'csv_cleanup': csv_result,
            'zip_cleanup': zip_result,
            'total_files_deleted': csv_result['files_deleted'] + zip_result['files_deleted'],
            'total_space_freed_bytes': csv_result['space_freed_bytes'] + zip_result['space_freed_bytes'],
            'total_failed_deletions': len(csv_result['failed_deletions']) + len(zip_result['failed_deletions'])
        }
        
        # Determine overall status
        if csv_result['status'] == 'failed' or zip_result['status'] == 'failed':
            combined_result['status'] = 'failed'
        elif csv_result['status'] == 'partial' or zip_result['status'] == 'partial':
            combined_result['status'] = 'partial'
        elif csv_result['status'] == 'success' and zip_result['status'] == 'success':
            combined_result['status'] = 'success'
        elif csv_result['status'] == 'no_files' and zip_result['status'] == 'no_files':
            combined_result['status'] = 'no_files'
        else:
            combined_result['status'] = 'partial'
        
        logger.info(f"Complete cleanup finished with status: {combined_result['status']}")
        logger.info(f"Total files deleted: {combined_result['total_files_deleted']}")
        logger.info(f"Total space freed: {combined_result['total_space_freed_bytes']} bytes ({combined_result['total_space_freed_bytes'] / (1024**3):.2f} GB)")
        
        return combined_result
    
    def get_disk_usage_info(self) -> Dict[str, any]:
        """
        Get information about disk usage in the downloads directory.
        
        Returns:
            Dictionary containing disk usage information
        """
        if not self.downloads_dir.exists():
            return {
                'directory_exists': False,
                'total_size_bytes': 0,
                'file_count': 0,
                'csv_files': 0,
                'zip_files': 0,
                'other_files': 0
            }
        
        total_size = 0
        file_count = 0
        csv_count = 0
        zip_count = 0
        other_count = 0
        
        for file_path in self.downloads_dir.rglob('*'):
            if file_path.is_file():
                try:
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    file_count += 1
                    
                    if file_path.suffix.lower() == '.csv':
                        csv_count += 1
                    elif file_path.suffix.lower() == '.zip':
                        zip_count += 1
                    else:
                        other_count += 1
                except Exception as e:
                    logger.warning(f"Could not get size for {file_path}: {e}")
        
        return {
            'directory_exists': True,
            'total_size_bytes': total_size,
            'file_count': file_count,
            'csv_files': csv_count,
            'zip_files': zip_count,
            'other_files': other_count
        } 