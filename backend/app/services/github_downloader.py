import requests
import os

class GitHubDownloader:
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.output_dir = os.path.join(os.getcwd(), "downloads_" + os.urandom(4).hex())

    def download_file(self, url: str) -> str:
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3.raw"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Extract file path from URL (between 'contents/' and '?ref')
            repo_path = url.split('/contents/')[1].split('?ref=')[0]
            file_path = os.path.join(self.output_dir, repo_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as file:
                file.write(response.content)
            return file_path
        else:
            raise Exception(f"Failed to download file: {response.status_code}")
