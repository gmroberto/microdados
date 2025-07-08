import zipfile
from pathlib import Path
from typing import List
from config import get_path

class ENEMExtractor:
    """Simplified ENEM microdata extractor."""
    
    def __init__(self):
        self.downloads_dir = get_path('downloads')
    
    def extract_all(self) -> bool:
        """Extract all ZIP files."""
        try:
            zip_files = list(self.downloads_dir.glob('*.zip'))
            
            if not zip_files:
                print("No ZIP files found to extract")
                return True
            
            print(f"Found {len(zip_files)} ZIP files to extract")
            
            for zip_path in zip_files:
                print(f"\nProcessing: {zip_path.name}")
                
                if not self._is_valid_zip(zip_path):
                    continue
                
                self._extract_zip(zip_path)
            
            return True
            
        except Exception as e:
            print(f"Error during extraction: {e}")
            return False
    
    def delete_zip_files(self) -> bool:
        """Delete all ZIP files after successful extraction."""
        try:
            zip_files = list(self.downloads_dir.glob('*.zip'))
            
            if not zip_files:
                print("No ZIP files found to delete")
                return True
            
            print(f"Found {len(zip_files)} ZIP files to delete")
            
            for zip_path in zip_files:
                print(f"\nDeleting: {zip_path.name}")
                self._delete_zip(zip_path)
            
            return True
            
        except Exception as e:
            print(f"Error during ZIP deletion: {e}")
            return False
    
    def extract_and_delete(self) -> bool:
        """Extract all ZIP files and delete them after extraction (legacy method)."""
        try:
            zip_files = list(self.downloads_dir.glob('*.zip'))
            
            if not zip_files:
                print("No ZIP files found to extract")
                return True
            
            print(f"Found {len(zip_files)} ZIP files to extract")
            
            for zip_path in zip_files:
                print(f"\nProcessing: {zip_path.name}")
                
                if not self._is_valid_zip(zip_path):
                    continue
                
                if self._extract_zip(zip_path):
                    self._delete_zip(zip_path)
            
            return True
            
        except Exception as e:
            print(f"Error during extraction: {e}")
            return False
    
    def _is_valid_zip(self, zip_path: Path) -> bool:
        """Check if ZIP file is valid."""
        if not zip_path.exists():
            print(f"Warning: {zip_path.name} does not exist")
            return False
        
        if zip_path.stat().st_size == 0:
            print(f"Warning: {zip_path.name} is empty, deleting...")
            self._delete_zip(zip_path)
            return False
        
        if not zipfile.is_zipfile(zip_path):
            print(f"Warning: {zip_path.name} is not a valid ZIP file, deleting...")
            self._delete_zip(zip_path)
            return False
        
        return True
    
    def _extract_zip(self, zip_path: Path) -> bool:
        """Extract a single ZIP file."""
        try:
            csv_extracted = False
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.filelist:
                    if self._should_extract_file(file_info):
                        if self._extract_csv_file(zip_ref, file_info):
                            csv_extracted = True
            
            return csv_extracted
            
        except zipfile.BadZipFile:
            print(f"Error: {zip_path.name} is corrupted, deleting...")
            self._delete_zip(zip_path)
            return False
        except Exception as e:
            print(f"Error processing {zip_path.name}: {e}")
            return False
    
    def _should_extract_file(self, file_info: zipfile.ZipInfo) -> bool:
        """Check if file should be extracted."""
        return (file_info.filename.endswith('.csv') and 
                'MICRODADOS' in file_info.filename.upper())
    
    def _extract_csv_file(self, zip_ref: zipfile.ZipFile, file_info: zipfile.ZipInfo) -> bool:
        """Extract a single CSV file from ZIP."""
        csv_name = Path(file_info.filename).name
        target_path = self.downloads_dir / csv_name
        
        # Skip if CSV already exists
        if target_path.exists():
            print(f"Skipping extraction: {csv_name} already exists")
            return True
        
        try:
            with open(target_path, 'wb') as f:
                f.write(zip_ref.read(file_info.filename))
            print(f"Extracted: {csv_name}")
            return True
        except Exception as e:
            print(f"Error extracting {csv_name}: {e}")
            return False
    
    def _delete_zip(self, zip_path: Path) -> None:
        """Delete a ZIP file."""
        try:
            zip_path.unlink()
            print(f"Deleted: {zip_path.name}")
        except Exception as e:
            print(f"Error deleting {zip_path.name}: {e}")
    
    def get_csv_files(self) -> List[Path]:
        """Get list of extracted CSV files."""
        return list(self.downloads_dir.glob('MICRODADOS_ENEM_*.csv')) 