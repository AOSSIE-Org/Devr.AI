import requests
import os

class GitHubDownloader:
    def __init__(self, github_token: str):
        self.github_token = github_token

    def download_file(self, owner: str, repo: str, path: str, output_dir: str) -> str:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3.raw"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            file_path = os.path.join(output_dir, path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as file:
                file.write(response.content)
            return file_path
        else:
            raise Exception(f"Failed to download file: {response.status_code}")
