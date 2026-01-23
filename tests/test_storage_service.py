"""Unit tests for StorageService class."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from services.storage import StorageService
from config import settings


class TestStorageService:
    """Tests for StorageService class."""
    
    @patch("services.storage.create_client")
    @patch("services.storage.settings")
    def test_storage_service_initialization(self, mock_settings, mock_create_client):
        """Test StorageService initialization."""
        mock_settings.supabase_url = "https://test.supabase.co"
        mock_settings.supabase_key = "test_key"
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        service = StorageService()
        
        assert service.supabase == mock_client
        assert service.storage == mock_client.storage
        mock_create_client.assert_called_once_with("https://test.supabase.co", "test_key")
    
    @patch("services.storage.settings")
    def test_storage_service_no_url(self, mock_settings):
        """Test StorageService initialization without URL."""
        mock_settings.supabase_url = None
        
        with pytest.raises(ValueError, match="SUPABASE_URL is not configured"):
            StorageService()
    
    @patch("services.storage.validate_file_type")
    @patch("services.storage.validate_file_size")
    @patch("services.storage.sanitize_filename")
    @patch("services.storage.generate_storage_path")
    @patch("services.storage.calculate_file_hash")
    @patch("services.storage.extract_file_metadata")
    @patch("services.storage.StorageConfig")
    @patch("services.storage.create_client")
    @patch("services.storage.settings")
    def test_upload_file_success(
        self, mock_settings, mock_create_client, mock_config, mock_extract,
        mock_hash, mock_path, mock_sanitize, mock_validate_size, mock_validate_type
    ):
        """Test successful file upload."""
        # Setup mocks
        mock_settings.supabase_url = "https://test.supabase.co"
        mock_settings.supabase_key = "test_key"
        mock_client = MagicMock()
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_client.storage = mock_storage
        mock_storage.from_.return_value = mock_bucket
        mock_bucket.upload.return_value = {"path": "test_path"}
        mock_create_client.return_value = mock_client
        
        mock_validate_type.return_value = (True, None)
        mock_validate_size.return_value = (True, None)
        mock_sanitize.return_value = "test.jpg"
        mock_path.return_value = "images/2024/01/test.jpg"
        mock_hash.return_value = "abc123"
        mock_extract.return_value = {"content_type": "image/jpeg"}
        mock_config.DEFAULT_BUCKETS = {"images": "images"}
        mock_config.is_public_bucket.return_value = True
        
        service = StorageService()
        result = service.upload_file(
            file_content=b"test content",
            filename="test.jpg",
            bucket_type="images",
            user_id="user123",
            make_public=True
        )
        
        assert result["storage_path"] == "images/2024/01/test.jpg"
        assert result["bucket_name"] == "images"
        assert result["file_hash"] == "abc123"
        mock_bucket.upload.assert_called_once()
    
    @patch("services.storage.validate_file_type")
    @patch("services.storage.create_client")
    @patch("services.storage.settings")
    def test_upload_file_invalid_type(
        self, mock_settings, mock_create_client, mock_validate_type
    ):
        """Test file upload with invalid file type."""
        mock_settings.supabase_url = "https://test.supabase.co"
        mock_settings.supabase_key = "test_key"
        mock_create_client.return_value = MagicMock()
        
        mock_validate_type.return_value = (False, "File type not allowed")
        
        service = StorageService()
        
        with pytest.raises(ValueError, match="File type not allowed"):
            service.upload_file(
                file_content=b"test",
                filename="test.pdf",
                bucket_type="images"
            )
    
    @patch("services.storage.validate_file_size")
    @patch("services.storage.validate_file_type")
    @patch("services.storage.create_client")
    @patch("services.storage.settings")
    def test_upload_file_too_large(
        self, mock_settings, mock_create_client, mock_validate_type, mock_validate_size
    ):
        """Test file upload with file too large."""
        mock_settings.supabase_url = "https://test.supabase.co"
        mock_settings.supabase_key = "test_key"
        mock_create_client.return_value = MagicMock()
        
        mock_validate_type.return_value = (True, None)
        mock_validate_size.return_value = (False, "File too large")
        
        service = StorageService()
        
        with pytest.raises(ValueError, match="File too large"):
            service.upload_file(
                file_content=b"x" * 10000000,
                filename="test.jpg",
                bucket_type="images"
            )
    
    @patch("services.storage.create_client")
    @patch("services.storage.settings")
    def test_download_file_success(self, mock_settings, mock_create_client):
        """Test successful file download."""
        mock_settings.supabase_url = "https://test.supabase.co"
        mock_settings.supabase_key = "test_key"
        mock_client = MagicMock()
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_client.storage = mock_storage
        mock_storage.from_.return_value = mock_bucket
        mock_bucket.download.return_value = b"file content"
        mock_create_client.return_value = mock_client
        
        service = StorageService()
        result = service.download_file("images/2024/01/test.jpg", "images")
        
        assert result == b"file content"
        mock_bucket.download.assert_called_once_with("images/2024/01/test.jpg")
    
    @patch("services.storage.create_client")
    @patch("services.storage.settings")
    def test_download_file_error(self, mock_settings, mock_create_client):
        """Test file download with error."""
        mock_settings.supabase_url = "https://test.supabase.co"
        mock_settings.supabase_key = "test_key"
        mock_client = MagicMock()
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_client.storage = mock_storage
        mock_storage.from_.return_value = mock_bucket
        mock_bucket.download.side_effect = Exception("Download failed")
        mock_create_client.return_value = mock_client
        
        service = StorageService()
        
        with pytest.raises(Exception, match="File download failed"):
            service.download_file("images/2024/01/test.jpg", "images")
    
    @patch("services.storage.create_client")
    @patch("services.storage.settings")
    def test_delete_file_success(self, mock_settings, mock_create_client):
        """Test successful file deletion."""
        mock_settings.supabase_url = "https://test.supabase.co"
        mock_settings.supabase_key = "test_key"
        mock_client = MagicMock()
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_client.storage = mock_storage
        mock_storage.from_.return_value = mock_bucket
        mock_bucket.remove.return_value = True
        mock_create_client.return_value = mock_client
        
        service = StorageService()
        result = service.delete_file("images/2024/01/test.jpg", "images")
        
        assert result is True
        mock_bucket.remove.assert_called_once_with(["images/2024/01/test.jpg"])
    
    @patch("services.storage.create_client")
    @patch("services.storage.settings")
    def test_list_files_success(self, mock_settings, mock_create_client):
        """Test successful file listing."""
        mock_settings.supabase_url = "https://test.supabase.co"
        mock_settings.supabase_key = "test_key"
        mock_client = MagicMock()
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_client.storage = mock_storage
        mock_storage.from_.return_value = mock_bucket
        mock_bucket.list.return_value = [{"name": "test1.jpg"}, {"name": "test2.jpg"}]
        mock_create_client.return_value = mock_client
        
        service = StorageService()
        result = service.list_files("images", folder_path="2024/01", limit=10)
        
        assert len(result) == 2
        mock_bucket.list.assert_called_once_with(path="2024/01", limit=10)
    
    @patch("services.storage.create_client")
    @patch("services.storage.settings")
    def test_list_files_error(self, mock_settings, mock_create_client):
        """Test file listing with error."""
        mock_settings.supabase_url = "https://test.supabase.co"
        mock_settings.supabase_key = "test_key"
        mock_client = MagicMock()
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_client.storage = mock_storage
        mock_storage.from_.return_value = mock_bucket
        mock_bucket.list.side_effect = Exception("List failed")
        mock_create_client.return_value = mock_client
        
        service = StorageService()
        result = service.list_files("images")
        
        assert result == []
    
    @patch("services.storage.create_client")
    @patch("services.storage.settings")
    def test_get_public_url(self, mock_settings, mock_create_client):
        """Test getting public URL."""
        mock_settings.supabase_url = "https://test.supabase.co"
        mock_settings.supabase_key = "test_key"
        mock_client = MagicMock()
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_client.storage = mock_storage
        mock_storage.from_.return_value = mock_bucket
        mock_bucket.get_public_url.return_value = "https://example.com/test.jpg"
        mock_create_client.return_value = mock_client
        
        service = StorageService()
        result = service.get_public_url("images/2024/01/test.jpg", "images")
        
        assert result == "https://example.com/test.jpg"
    
    @patch("services.storage.create_client")
    @patch("services.storage.settings")
    def test_get_signed_url(self, mock_settings, mock_create_client):
        """Test getting signed URL."""
        mock_settings.supabase_url = "https://test.supabase.co"
        mock_settings.supabase_key = "test_key"
        mock_client = MagicMock()
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_client.storage = mock_storage
        mock_storage.from_.return_value = mock_bucket
        mock_bucket.create_signed_url.return_value = {"signedURL": "https://example.com/signed.jpg"}
        mock_create_client.return_value = mock_client
        
        service = StorageService()
        result = service.get_signed_url("images/2024/01/test.jpg", "images", expires_in=7200)
        
        assert result == "https://example.com/signed.jpg"
        mock_bucket.create_signed_url.assert_called_once_with(
            path="images/2024/01/test.jpg",
            expires_in=7200
        )

