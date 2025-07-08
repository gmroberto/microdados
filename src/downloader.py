import requests
import time
import json
import urllib3
from pathlib import Path
from typing import List, Optional
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import get_url, get_path, config_manager

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ENEMDownloader:
    """Simplified ENEM microdata downloader."""
    
    def __init__(self):
        self.downloads_dir = get_path('downloads')
        self.downloads_dir.mkdir(exist_ok=True)
        # Use downloads directory for history file to ensure write permissions
        self.history_file = self.downloads_dir / "download_history.json"
        self.history = self._load_history()
        
        # Create a session with better connection handling
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Configure connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=3
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def _load_history(self) -> dict:
        """Load download history from JSON file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {}
    
    def _save_history(self) -> None:
        """Save download history to JSON file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)
    
    def _get_download_links(self) -> List[str]:
        """Get all ENEM microdata download links."""
        try:
            response = self.session.get(get_url('enem_base_url'), timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', class_='external-link', href=True)
            
            return [
                link['href'] for link in links
                if 'microdados_enem' in link['href'].lower() and link['href'].endswith('.zip')
            ]
        except requests.RequestException as e:
            print(f"Error fetching download links: {e}")
            return []
    
    def _is_downloaded(self, download_url: str) -> bool:
        """Check if file is already downloaded."""
        zip_filename = download_url.split('/')[-1]
        csv_filename = zip_filename.replace('.zip', '.csv')
        
        zip_path = self.downloads_dir / zip_filename
        csv_path = self.downloads_dir / csv_filename
        
        return zip_path.exists() or csv_path.exists()
    
    def _download_with_progress(self, response: requests.Response, file_path: Path) -> None:
        """Download file with progress tracking."""
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"Progress: {progress:.1f}%", end='\r')
        print()
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((requests.RequestException, IOError, ConnectionResetError))
    )
    def _download_file(self, download_url: str) -> bool:
        """Download a single file with retry logic."""
        if self._is_downloaded(download_url):
            print(f"File already exists: {download_url.split('/')[-1]}")
            return True
        
        filename = self.downloads_dir / download_url.split('/')[-1]
        
        try:
            print(f"Downloading: {filename.name}")
            response = self.session.get(download_url, stream=True, timeout=300)
            response.raise_for_status()
            
            self._download_with_progress(response, filename)
            
            # Update history
            self.history[download_url] = {
                'filename': str(filename),
                'download_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            self._save_history()
            
            print(f"Successfully downloaded: {filename.name}")
            return True
            
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error downloading {download_url}: {e}")
            raise
        except requests.exceptions.Timeout as e:
            print(f"Timeout error downloading {download_url}: {e}")
            raise
        except Exception as e:
            print(f"Error downloading {download_url}: {e}")
            return False
    
    def download_all(self, years: Optional[List[str]] = None) -> None:
        """Download all ENEM microdata files."""
        print("Fetching download links...")
        download_links = self._get_download_links()
        
        if not download_links:
            print("No download links found!")
            return
        
        # Filter by years if specified
        if years:
            download_links = [
                link for link in download_links 
                if any(year in link for year in years)
            ]
            if not download_links:
                print(f"No downloads found for specified years: {years}")
                return
        
        print(f"Found {len(download_links)} files to download")
        
        successful_downloads = 0
        failed_downloads = []
        
        for i, download_url in enumerate(download_links, 1):
            print(f"\nDownloading file {i} of {len(download_links)}")
            try:
                success = self._download_file(download_url)
                if success:
                    successful_downloads += 1
                else:
                    failed_downloads.append(download_url)
            except Exception as e:
                print(f"Failed to download {download_url}: {e}")
                failed_downloads.append(download_url)
            
            if i < len(download_links):
                print("Waiting 3 seconds before next download...")
                time.sleep(3)  # Be polite to the server
        
        print(f"\nDownload summary:")
        print(f"Successfully downloaded: {successful_downloads}")
        print(f"Failed downloads: {len(failed_downloads)}")
        
        if failed_downloads:
            print("\nFailed downloads:")
            for url in failed_downloads:
                print(f"  - {url}")
    
    def download_file(self, download_url: str) -> bool:
        """Download a single file by URL."""
        return self._download_file(download_url)
    
    def download_by_year(self, year: str) -> None:
        """Download files for a specific year."""
        self.download_all(years=[year]) 