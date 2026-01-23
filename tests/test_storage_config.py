"""Unit tests for storage configuration."""

import pytest
from config.storage import StorageConfig


class TestStorageConfig:
    """Tests for StorageConfig class."""
    
    def test_default_buckets(self):
        """Test default bucket names."""
        assert "artifacts" in StorageConfig.DEFAULT_BUCKETS
        assert "documents" in StorageConfig.DEFAULT_BUCKETS
        assert "images" in StorageConfig.DEFAULT_BUCKETS
        assert StorageConfig.DEFAULT_BUCKETS["artifacts"] == "artifacts"
        assert StorageConfig.DEFAULT_BUCKETS["documents"] == "documents"
        assert StorageConfig.DEFAULT_BUCKETS["images"] == "images"
    
    def test_file_size_limits(self):
        """Test file size limits."""
        assert StorageConfig.MAX_FILE_SIZE == 100 * 1024 * 1024  # 100 MB
        assert StorageConfig.MAX_IMAGE_SIZE == 10 * 1024 * 1024  # 10 MB
        assert StorageConfig.MAX_DOCUMENT_SIZE == 50 * 1024 * 1024  # 50 MB
        assert StorageConfig.MAX_ARTIFACT_SIZE == 100 * 1024 * 1024  # 100 MB
    
    def test_allowed_image_types(self):
        """Test allowed image types."""
        assert "image/jpeg" in StorageConfig.ALLOWED_IMAGE_TYPES
        assert "image/png" in StorageConfig.ALLOWED_IMAGE_TYPES
        assert "image/gif" in StorageConfig.ALLOWED_IMAGE_TYPES
        assert "image/webp" in StorageConfig.ALLOWED_IMAGE_TYPES
    
    def test_allowed_document_types(self):
        """Test allowed document types."""
        assert "application/pdf" in StorageConfig.ALLOWED_DOCUMENT_TYPES
        assert "text/plain" in StorageConfig.ALLOWED_DOCUMENT_TYPES
        assert "text/csv" in StorageConfig.ALLOWED_DOCUMENT_TYPES
    
    def test_allowed_artifact_types(self):
        """Test allowed artifact types."""
        assert "application/zip" in StorageConfig.ALLOWED_ARTIFACT_TYPES
        assert "application/json" in StorageConfig.ALLOWED_ARTIFACT_TYPES
        assert "text/plain" in StorageConfig.ALLOWED_ARTIFACT_TYPES
    
    def test_get_allowed_types_images(self):
        """Test get_allowed_types for images."""
        types = StorageConfig.get_allowed_types("images")
        assert isinstance(types, list)
        assert "image/jpeg" in types
        assert "image/png" in types
    
    def test_get_allowed_types_documents(self):
        """Test get_allowed_types for documents."""
        types = StorageConfig.get_allowed_types("documents")
        assert isinstance(types, list)
        assert "application/pdf" in types
    
    def test_get_allowed_types_artifacts(self):
        """Test get_allowed_types for artifacts."""
        types = StorageConfig.get_allowed_types("artifacts")
        assert isinstance(types, list)
        assert "application/zip" in types
    
    def test_get_allowed_types_unknown(self):
        """Test get_allowed_types for unknown bucket type."""
        types = StorageConfig.get_allowed_types("unknown")
        assert types == []
    
    def test_get_max_size_images(self):
        """Test get_max_size for images."""
        max_size = StorageConfig.get_max_size("images")
        assert max_size == StorageConfig.MAX_IMAGE_SIZE
    
    def test_get_max_size_documents(self):
        """Test get_max_size for documents."""
        max_size = StorageConfig.get_max_size("documents")
        assert max_size == StorageConfig.MAX_DOCUMENT_SIZE
    
    def test_get_max_size_artifacts(self):
        """Test get_max_size for artifacts."""
        max_size = StorageConfig.get_max_size("artifacts")
        assert max_size == StorageConfig.MAX_ARTIFACT_SIZE
    
    def test_get_max_size_unknown(self):
        """Test get_max_size for unknown bucket type."""
        max_size = StorageConfig.get_max_size("unknown")
        assert max_size == StorageConfig.MAX_FILE_SIZE
    
    def test_is_public_bucket(self):
        """Test is_public_bucket method."""
        assert StorageConfig.is_public_bucket("images") is True
        assert StorageConfig.is_public_bucket("documents") is False
        assert StorageConfig.is_public_bucket("artifacts") is False
        assert StorageConfig.is_public_bucket("unknown") is False
    
    def test_folder_structure(self):
        """Test folder structure configuration."""
        assert "images" in StorageConfig.FOLDER_STRUCTURE
        assert "documents" in StorageConfig.FOLDER_STRUCTURE
        assert "artifacts" in StorageConfig.FOLDER_STRUCTURE
        assert "{year}" in StorageConfig.FOLDER_STRUCTURE["images"]
        assert "{month}" in StorageConfig.FOLDER_STRUCTURE["images"]

