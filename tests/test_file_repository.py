"""Unit tests for FileRepository."""

import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from models.file import File
from repositories.file import FileRepository


class TestFileRepository:
    """Tests for FileRepository class."""
    
    def test_file_repository_initialization(self):
        """Test FileRepository initialization."""
        repo = FileRepository()
        assert repo.model == File
    
    def test_get_by_storage_path(self, test_session):
        """Test get_by_storage_path method."""
        repo = FileRepository()
        mock_file = File(
            id=1,
            filename="test.jpg",
            storage_path="images/2024/01/test.jpg",
            size=1024,
            content_type="image/jpeg",
            bucket_name="images",
            bucket_type="images"
        )
        
        repo.get_by_field = MagicMock(return_value=mock_file)
        
        result = repo.get_by_storage_path(test_session, "images/2024/01/test.jpg")
        
        assert result == mock_file
        repo.get_by_field.assert_called_once_with(test_session, "storage_path", "images/2024/01/test.jpg")
    
    def test_get_by_hash(self, test_session):
        """Test get_by_hash method."""
        repo = FileRepository()
        mock_file = File(
            id=1,
            filename="test.jpg",
            storage_path="images/2024/01/test.jpg",
            size=1024,
            content_type="image/jpeg",
            bucket_name="images",
            bucket_type="images",
            file_hash="abc123"
        )
        
        repo.get_by_field = MagicMock(return_value=mock_file)
        
        result = repo.get_by_hash(test_session, "abc123")
        
        assert result == mock_file
        repo.get_by_field.assert_called_once_with(test_session, "file_hash", "abc123")
    
    def test_get_by_user(self, test_session):
        """Test get_by_user method."""
        repo = FileRepository()
        mock_files = [
            File(id=1, filename="test1.jpg", storage_path="path1", size=1024, content_type="image/jpeg", bucket_name="images", bucket_type="images", uploaded_by="user123"),
            File(id=2, filename="test2.jpg", storage_path="path2", size=2048, content_type="image/jpeg", bucket_name="images", bucket_type="images", uploaded_by="user123")
        ]
        
        repo.get_multi = MagicMock(return_value=mock_files)
        
        result = repo.get_by_user(test_session, "user123", skip=0, limit=10)
        
        assert result == mock_files
        repo.get_multi.assert_called_once_with(test_session, skip=0, limit=10, filters={"uploaded_by": "user123"})
    
    def test_get_by_bucket(self, test_session):
        """Test get_by_bucket method."""
        repo = FileRepository()
        mock_files = [
            File(id=1, filename="test1.jpg", storage_path="path1", size=1024, content_type="image/jpeg", bucket_name="images", bucket_type="images")
        ]
        
        repo.get_multi = MagicMock(return_value=mock_files)
        
        result = repo.get_by_bucket(test_session, "images", skip=0, limit=10)
        
        assert result == mock_files
        repo.get_multi.assert_called_once_with(test_session, skip=0, limit=10, filters={"bucket_name": "images"})
    
    def test_get_public_files(self, test_session):
        """Test get_public_files method."""
        repo = FileRepository()
        mock_files = [
            File(id=1, filename="test1.jpg", storage_path="path1", size=1024, content_type="image/jpeg", bucket_name="images", bucket_type="images", is_public=True)
        ]
        
        repo.get_multi = MagicMock(return_value=mock_files)
        
        result = repo.get_public_files(test_session, skip=0, limit=10)
        
        assert result == mock_files
        repo.get_multi.assert_called_once_with(test_session, skip=0, limit=10, filters={"is_public": True})

