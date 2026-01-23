"""Unit tests for File model."""

import pytest
from datetime import datetime
from models.file import File
from models.base import BaseModel


class TestFileModel:
    """Tests for File model class."""
    
    def test_file_inherits_from_base_model(self):
        """Test that File inherits from BaseModel."""
        assert issubclass(File, BaseModel)
    
    def test_file_has_required_fields(self):
        """Test that File has required fields."""
        file = File(
            filename="test.jpg",
            storage_path="images/2024/01/test.jpg",
            size=1024,
            content_type="image/jpeg",
            bucket_name="images",
            bucket_type="images"
        )
        
        assert file.filename == "test.jpg"
        assert file.storage_path == "images/2024/01/test.jpg"
        assert file.size == 1024
        assert file.content_type == "image/jpeg"
        assert file.bucket_name == "images"
        assert file.bucket_type == "images"
    
    def test_file_has_optional_fields(self):
        """Test that File has optional fields."""
        file = File(
            filename="test.jpg",
            storage_path="images/2024/01/test.jpg",
            size=1024,
            content_type="image/jpeg",
            bucket_name="images",
            bucket_type="images",
            file_hash="abc123",
            uploaded_by="user123",
            is_public=True,
            file_metadata={"key": "value"}
        )
        
        assert file.file_hash == "abc123"
        assert file.uploaded_by == "user123"
        assert file.is_public is True
        assert file.file_metadata == {"key": "value"}
    
    def test_file_defaults(self):
        """Test File default values."""
        file = File(
            filename="test.jpg",
            storage_path="images/2024/01/test.jpg",
            size=1024,
            content_type="image/jpeg",
            bucket_name="images",
            bucket_type="images"
        )
        
        assert file.file_hash is None
        assert file.uploaded_by is None
        assert file.is_public is False
        assert file.file_metadata is None
        assert file.id is None
        assert isinstance(file.created_at, datetime)
        assert isinstance(file.updated_at, datetime)
    
    def test_file_table_name(self):
        """Test that File has correct table name."""
        assert File.__tablename__ == "files"
    
    def test_file_metadata_json_field(self):
        """Test that file_metadata can store JSON data."""
        metadata = {
            "width": 1920,
            "height": 1080,
            "tags": ["photo", "nature"]
        }
        
        file = File(
            filename="test.jpg",
            storage_path="images/2024/01/test.jpg",
            size=1024,
            content_type="image/jpeg",
            bucket_name="images",
            bucket_type="images",
            file_metadata=metadata
        )
        
        assert file.file_metadata == metadata
        assert file.file_metadata["width"] == 1920

