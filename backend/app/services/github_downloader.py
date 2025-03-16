import requests
import os
from typing import List
import shutil

class GitHubDownloader:
    def __init__(self, github_token: str):
        """
        Initialize the GitHub downloader with authentication token.
        
        Args:
            github_token (str): GitHub authentication token for API requests
        """
        self.github_token = github_token
        timestamp = str(int(os.path.getmtime(__file__)))
        random_suffix = os.urandom(4).hex()
        self.output_dir = os.path.join("/tmp", f"github_downloads_{timestamp}_{random_suffix}")
        # Ensure the directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def _download_file(self, url: str) -> str:
        """
        Download a single file from GitHub repository.
        
        Args:
            url (str): GitHub API URL for the file
            
        Returns:
            str: Local path where the file was saved
            
        Raises:
            Exception: If download fails due to API error or network issues
        """
        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3.raw"
            }
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Extract file path from URL (between 'contents/' and '?ref')
                repo_path = url.split('/contents/')[1].split('?ref=')[0]
                file_path = os.path.join(self.output_dir, repo_path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                return file_path
            elif response.status_code == 401:
                raise Exception("Authentication failed: Invalid GitHub token")
            elif response.status_code == 403:
                raise Exception("API rate limit exceeded or permission denied")
            elif response.status_code == 404:
                raise Exception(f"File not found: {url}")
            else:
                raise Exception(f"Failed to download file: HTTP {response.status_code}")
        except requests.RequestException as e:
            raise Exception(f"Network error while downloading {url}: {str(e)}")
        except Exception as e:
            raise Exception(f"Error downloading {url}: {str(e)}")

    def _download_files(self, urls: List[str]) -> List[str]:
        """
        Download multiple files from GitHub repository.
        
        Args:
            urls (List[str]): List of GitHub API URLs for files
            
        Returns:
            List[str]: List of local paths where files were saved
        """
        downloaded_files = []
        for url in urls:
            try:
                file_path = self._download_file(url)
                downloaded_files.append(file_path)
            except Exception as e:
                print(f"Warning: Failed to download {url}: {str(e)}")
        return downloaded_files
    
    def _delete_downloaded_file(self, file_path: str):
        """
        Delete a downloaded file and its empty parent directories.
        
        Args:
            file_path (str): Path to the file to delete
        """
        try:
            # Remove the file after reading its content to avoid clutter
            if os.path.exists(file_path):
                os.remove(file_path)
                
            # Check if the directory is empty and remove it if it is
            dir_path = os.path.dirname(file_path)
            if os.path.exists(dir_path) and not os.listdir(dir_path):
                os.rmdir(dir_path)
                
                # Also try to remove parent directories if they become empty
                parent_dir = os.path.dirname(dir_path)
                while parent_dir and parent_dir != self.output_dir and os.path.exists(parent_dir):
                    if not os.listdir(parent_dir):
                        os.rmdir(parent_dir)
                        parent_dir = os.path.dirname(parent_dir)
                    else:
                        break
        except Exception as e:
            print(f"Warning: Failed to delete {file_path}: {str(e)}")

    def __del__(self):
        """
        Destructor to clean up temporary files when the instance is garbage collected.
        Deletes the entire output directory and its contents.
        """
        try:
            if os.path.exists(self.output_dir):
                shutil.rmtree(self.output_dir)
        except Exception as e:
            print(f"Warning: Failed to delete output directory {self.output_dir}: {str(e)}")