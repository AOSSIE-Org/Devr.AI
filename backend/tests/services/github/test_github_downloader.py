import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import requests

# Import the module to test
from app.services.github.github_downloader import GitHubDownloader

class TestGitHubDownloader(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Use environment variable or a test token
        self.github_token = os.getenv("GITHUB_TOKEN", "test_token")
        self.downloader = GitHubDownloader(self.github_token)
        
        # Create a test directory structure for deletion tests
        self.test_dir = tempfile.mkdtemp()
        self.test_subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(self.test_subdir, exist_ok=True)
        self.test_file = os.path.join(self.test_subdir, "test_file.txt")
        with open(self.test_file, 'w') as f:
            f.write("test content")
    
    def tearDown(self):
        """Clean up after each test method."""
        # Ensure test directory is removed if it still exists
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """Test initialization of GitHubDownloader."""
        self.assertEqual(self.downloader.github_token, self.github_token)
        self.assertTrue(os.path.exists(self.downloader.output_dir))
        self.assertTrue(self.downloader.output_dir.startswith("/tmp/github_downloads_"))
    
    @patch('requests.get')
    def test_download_file_success(self, mock_get):
        """Test downloading a single file successfully."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"test content"
        mock_get.return_value = mock_response
        
        # Test URL
        test_url = "https://api.github.com/repos/user/repo/contents/file.py?ref=main"
        
        # Call the method
        file_path = self.downloader._download_file(test_url)
        
        # Assertions
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(file_path.endswith("file.py"))
        self.assertEqual(os.path.join(self.downloader.output_dir, "file.py"), file_path)
        
        # Clean up
        os.remove(file_path)
    
    @patch('requests.get')
    def test_download_file_with_nested_path(self, mock_get):
        """Test downloading a file with a nested path."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"test content"
        mock_get.return_value = mock_response
        
        # Test URL with nested path
        test_url = "https://api.github.com/repos/user/repo/contents/dir1/dir2/file.py?ref=main"
        
        # Call the method
        file_path = self.downloader._download_file(test_url)
        
        # Assertions
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(file_path.endswith("dir1/dir2/file.py"))
        expected_path = os.path.join(self.downloader.output_dir, "dir1/dir2/file.py")
        self.assertEqual(expected_path, file_path)
        
        # Clean up
        os.remove(file_path)
        os.rmdir(os.path.dirname(file_path))
        os.rmdir(os.path.dirname(os.path.dirname(file_path)))
    
    @patch('requests.get')
    def test_download_file_unauthorized(self, mock_get):
        """Test downloading a file with invalid token."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        # Test URL
        test_url = "https://api.github.com/repos/user/repo/contents/file.py?ref=main"
        
        # Call the method
        with self.assertRaises(Exception) as context:
            self.downloader._download_file(test_url)
        
        self.assertIn("Authentication failed", str(context.exception))
    
    @patch('requests.get')
    def test_download_file_not_found(self, mock_get):
        """Test downloading a file that doesn't exist."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Test URL
        test_url = "https://api.github.com/repos/user/repo/contents/nonexistent.py?ref=main"
        
        # Call the method
        with self.assertRaises(Exception) as context:
            self.downloader._download_file(test_url)
        
        self.assertIn("File not found", str(context.exception))
    
    @patch('requests.get')
    def test_download_file_network_error(self, mock_get):
        """Test handling of network errors during download."""
        # Mock the response to raise an exception
        mock_get.side_effect = requests.RequestException("Network error")
        
        # Test URL
        test_url = "https://api.github.com/repos/user/repo/contents/file.py?ref=main"
        
        # Call the method
        with self.assertRaises(Exception) as context:
            self.downloader._download_file(test_url)
        
        self.assertIn("Network error", str(context.exception))
    
    def test_delete_downloaded_file(self):
        """Test deleting a downloaded file and its empty parent directories."""
        # Call the method
        self.downloader._delete_downloaded_file(self.test_file)
        
        # Assertions
        self.assertFalse(os.path.exists(self.test_file))
        self.assertFalse(os.path.exists(self.test_subdir))
        self.assertFalse(os.path.exists(self.test_dir))
    
    def test_delete_downloaded_file_with_siblings(self):
        """Test that parent directories with other files are not deleted."""
        # Create a sibling file
        sibling_file = os.path.join(self.test_subdir, "sibling.txt")
        with open(sibling_file, 'w') as f:
            f.write("sibling content")
        
        # Call the method
        self.downloader._delete_downloaded_file(self.test_file)
        
        # Assertions
        self.assertFalse(os.path.exists(self.test_file))
        self.assertTrue(os.path.exists(sibling_file))
        self.assertTrue(os.path.exists(self.test_subdir))
        self.assertTrue(os.path.exists(self.test_dir))
    
    @patch('shutil.rmtree')
    def test_destructor(self, mock_rmtree):
        """Test the destructor cleans up the output directory."""
        # Create a temporary downloader to test __del__
        temp_downloader = GitHubDownloader("test_token")
        output_dir = temp_downloader.output_dir
        
        # Call the destructor
        temp_downloader.__del__()
        
        # Assertions
        mock_rmtree.assert_called_once_with(output_dir)

    @patch('requests.get')
    def test_download_directory(self, mock_get):
        """Test downloading a directory recursively."""
        # Mock the responses
        dir_response = MagicMock()
        dir_response.status_code = 200
        dir_response.json.return_value = [
            {
                "type": "file",
                "name": "file1.py",
                "download_url": "https://api.github.com/repos/user/repo/contents/dir/file1.py?ref=main",
                "url": "https://api.github.com/repos/user/repo/contents/dir/file1.py?ref=main"
            },
            {
                "type": "dir",
                "name": "subdir",
                "url": "https://api.github.com/repos/user/repo/contents/dir/subdir?ref=main"
            }
        ]
        
        subdir_response = MagicMock()
        subdir_response.status_code = 200
        subdir_response.json.return_value = [
            {
                "type": "file",
                "name": "file2.py",
                "download_url": "https://api.github.com/repos/user/repo/contents/dir/subdir/file2.py?ref=main",
                "url": "https://api.github.com/repos/user/repo/contents/dir/subdir/file2.py?ref=main"
            }
        ]
        
        file_response = MagicMock()
        file_response.status_code = 200
        file_response.content = b"test content"
        
        # Set up the mock to return different responses for different URLs
        def side_effect(url, headers=None, timeout=None):
            if url == "https://api.github.com/repos/user/repo/contents/dir?ref=main":
                return dir_response
            elif url == "https://api.github.com/repos/user/repo/contents/dir/subdir?ref=main":
                return subdir_response
            else:
                return file_response
        
        mock_get.side_effect = side_effect
        
        # Test URL
        test_url = "https://api.github.com/repos/user/repo/contents/dir?ref=main"
        
        # Call the method
        result = self.downloader._download_directory(test_url)
        
        # Assertions
        self.assertEqual(2, len(result))
        self.assertTrue(any(path.endswith("dir/file1.py") for path in result))
        self.assertTrue(any(path.endswith("dir/subdir/file2.py") for path in result))
        
        # Clean up
        for path in result:
            if os.path.exists(path):
                os.remove(path)
                parent_dir = os.path.dirname(path)
                if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                    os.rmdir(parent_dir)
                    parent_dir = os.path.dirname(parent_dir)
                    if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                        os.rmdir(parent_dir)

    @patch('requests.get')
    def test_download_from_github(self, mock_get):
        """Test the download_from_github method."""
        # Mock the responses for a file
        file_check_response = MagicMock()
        file_check_response.status_code = 200
        file_check_response.json.return_value = {
            "type": "file",
            "name": "file.py",
            "download_url": "https://api.github.com/repos/user/repo/contents/file.py?ref=main"
        }
        
        file_content_response = MagicMock()
        file_content_response.status_code = 200
        file_content_response.content = b"test content"
        
        # Set up mock responses
        mock_get.side_effect = [file_check_response, file_content_response]
        
        # Test URL
        test_url = "https://api.github.com/repos/user/repo/contents/file.py?ref=main"
        
        # Call the method
        result = self.downloader.download_from_github(test_url)
        
        # Assertions
        self.assertEqual(1, len(result))
        self.assertTrue(os.path.exists(result[0]))
        
        # Clean up
        os.remove(result[0])

if __name__ == '__main__':
    unittest.main()