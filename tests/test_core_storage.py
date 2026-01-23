"""Unit tests for core storage utility functions."""

import pytest
import hashlib
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from core.storage import (
    get_file_extension,
    get_mime_type,
    validate_file_type,
    validate_file_size,
    generate_storage_path,
    sanitize_filename,
    calculate_file_hash,
    extract_file_metadata,
)


class TestGetFileExtension:
    """Tests for get_file_extension function."""
    
    def test_get_file_extension_with_dot(self):
        """Test getting extension from filename with dot."""
        assert get_file_extension("test.jpg") == "jpg"
        assert get_file_extension("test.PNG") == "png"  # Lowercase
        assert get_file_extension("file.name.pdf") == "pdf"
    
    def test_get_file_extension_no_extension(self):
        """Test getting extension from filename without extension."""
        assert get_file_extension("testfile") == ""
        assert get_file_extension("test.") == ""
    
    def test_get_file_extension_multiple_dots(self):
        """Test getting extension with multiple dots."""
        assert get_file_extension("file.name.tar.gz") == "gz"


class TestGetMimeType:
    """Tests for get_mime_type function."""
    
    def test_get_mime_type_known_types(self):
        """Test getting MIME type for known file types."""
        assert get_mime_type("test.jpg") == "image/jpeg"
        assert get_mime_type("test.png") == "image/png"
        assert get_mime_type("test.pdf") == "application/pdf"
        assert get_mime_type("test.txt") == "text/plain"
    
    def test_get_mime_type_unknown_type(self):
        """Test getting MIME type for unknown file type."""
        mime_type = get_mime_type("test.unknown")
        assert mime_type == "application/octet-stream"


class TestValidateFileType:
    """Tests for validate_file_type function."""
    
    def test_validate_file_type_valid_image(self):
        """Test validating a valid image file."""
        is_valid, error = validate_file_type("test.jpg", "images")
        assert is_valid is True
        assert error is None
    
    def test_validate_file_type_invalid_image(self):
        """Test validating an invalid image file."""
        is_valid, error = validate_file_type("test.pdf", "images")
        assert is_valid is False
        assert error is not None
        assert "not allowed" in error.lower()
    
    def test_validate_file_type_with_content_type(self):
        """Test validating with explicit content type."""
        is_valid, error = validate_file_type("test.jpg", "images", content_type="image/jpeg")
        assert is_valid is True
    
    def test_validate_file_type_document(self):
        """Test validating document file."""
        is_valid, error = validate_file_type("test.pdf", "documents")
        assert is_valid is True
    
    def test_validate_file_type_artifact(self):
        """Test validating artifact file."""
        is_valid, error = validate_file_type("test.zip", "artifacts")
        assert is_valid is True


class TestValidateFileSize:
    """Tests for validate_file_size function."""
    
    def test_validate_file_size_valid(self):
        """Test validating a valid file size."""
        is_valid, error = validate_file_size(5 * 1024 * 1024, "images")  # 5 MB
        assert is_valid is True
        assert error is None
    
    def test_validate_file_size_too_large(self):
        """Test validating a file that's too large."""
        is_valid, error = validate_file_size(20 * 1024 * 1024, "images")  # 20 MB > 10 MB limit
        assert is_valid is False
        assert error is not None
        assert "exceeds" in error.lower()
    
    def test_validate_file_size_empty(self):
        """Test validating an empty file."""
        is_valid, error = validate_file_size(0, "images")
        assert is_valid is False
        assert error is not None
        assert "empty" in error.lower()
    
    def test_validate_file_size_documents(self):
        """Test validating document file size."""
        is_valid, error = validate_file_size(30 * 1024 * 1024, "documents")  # 30 MB
        assert is_valid is True


class TestGenerateStoragePath:
    """Tests for generate_storage_path function."""
    
    def test_generate_storage_path_basic(self):
        """Test generating a basic storage path."""
        path = generate_storage_path("test.jpg", "images")
        assert "images" in path
        assert "test" in path
        assert ".jpg" in path
        assert str(datetime.utcnow().year) in path
    
    def test_generate_storage_path_with_user_id(self):
        """Test generating storage path with user ID."""
        path = generate_storage_path("test.jpg", "images", user_id="user123")
        assert "user123" in path
        assert "images" in path
    
    def test_generate_storage_path_includes_timestamp(self):
        """Test that storage path includes timestamp."""
        path = generate_storage_path("test.jpg", "images")
        # Should contain timestamp (numeric)
        assert any(char.isdigit() for char in path)
    
    def test_generate_storage_path_documents(self):
        """Test generating path for documents."""
        path = generate_storage_path("document.pdf", "documents")
        assert "documents" in path
        assert "document" in path


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""
    
    def test_sanitize_filename_safe(self):
        """Test sanitizing a safe filename."""
        filename = sanitize_filename("test.jpg")
        assert filename == "test.jpg"
    
    def test_sanitize_filename_with_path(self):
        """Test sanitizing filename with path components."""
        filename = sanitize_filename("/path/to/file.jpg")
        assert filename == "file.jpg"
        assert "/" not in filename
    
    def test_sanitize_filename_unsafe_chars(self):
        """Test sanitizing filename with unsafe characters."""
        filename = sanitize_filename("test<>file.jpg")
        assert "<" not in filename
        assert ">" not in filename
        assert "_" in filename
    
    def test_sanitize_filename_long(self):
        """Test sanitizing a very long filename."""
        long_name = "a" * 300 + ".jpg"
        filename = sanitize_filename(long_name)
        assert len(filename) <= 255
    
    def test_sanitize_filename_dots(self):
        """Test sanitizing filename with path traversal."""
        filename = sanitize_filename("../../../etc/passwd")
        assert ".." not in filename
        assert "/" not in filename


class TestCalculateFileHash:
    """Tests for calculate_file_hash function."""
    
    def test_calculate_file_hash(self):
        """Test calculating file hash."""
        content = b"test content"
        hash_value = calculate_file_hash(content)
        
        # Should be SHA-256 hex digest
        assert len(hash_value) == 64  # SHA-256 produces 64 hex characters
        assert isinstance(hash_value, str)
        
        # Verify it's the correct hash
        expected_hash = hashlib.sha256(content).hexdigest()
        assert hash_value == expected_hash
    
    def test_calculate_file_hash_different_content(self):
        """Test that different content produces different hashes."""
        hash1 = calculate_file_hash(b"content1")
        hash2 = calculate_file_hash(b"content2")
        assert hash1 != hash2
    
    def test_calculate_file_hash_same_content(self):
        """Test that same content produces same hash."""
        content = b"same content"
        hash1 = calculate_file_hash(content)
        hash2 = calculate_file_hash(content)
        assert hash1 == hash2


class TestExtractFileMetadata:
    """Tests for extract_file_metadata function."""
    
    def test_extract_file_metadata_basic(self):
        """Test extracting basic file metadata."""
        metadata = extract_file_metadata("test.jpg", 1024, "image/jpeg")
        
        assert metadata["filename"] == "test.jpg"
        assert metadata["size"] == 1024
        assert metadata["content_type"] == "image/jpeg"
        assert "extension" in metadata
        assert "uploaded_at" in metadata
    
    def test_extract_file_metadata_without_content_type(self):
        """Test extracting metadata without explicit content type."""
        metadata = extract_file_metadata("test.jpg", 1024)
        
        assert metadata["content_type"] is not None
        assert metadata["extension"] == "jpg"
    
    def test_extract_file_metadata_includes_timestamp(self):
        """Test that metadata includes upload timestamp."""
        metadata = extract_file_metadata("test.jpg", 1024)
        
        assert "uploaded_at" in metadata
        assert isinstance(metadata["uploaded_at"], str)

