"""Unit tests for Pydantic schemas."""

import pytest
from schemas.common import (
    BaseResponse,
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
    MessageResponse,
)
from schemas.storage import (
    FileUploadRequest,
    FileUploadResponse,
    FileDownloadResponse,
    FileInfo,
    FileListResponse,
    FileDeleteResponse,
)


class TestBaseResponse:
    """Tests for BaseResponse schema."""
    
    def test_base_response_creation(self):
        """Test creating BaseResponse."""
        response = BaseResponse(success=True, message="Test", data={"key": "value"})
        assert response.success is True
        assert response.message == "Test"
        assert response.data == {"key": "value"}
    
    def test_base_response_optional_fields(self):
        """Test BaseResponse with optional fields."""
        response = BaseResponse(success=False)
        assert response.success is False
        assert response.message is None
        assert response.data is None


class TestSuccessResponse:
    """Tests for SuccessResponse schema."""
    
    def test_success_response_default(self):
        """Test SuccessResponse with default success value."""
        response = SuccessResponse(message="Success", data={"result": "ok"})
        assert response.success is True
        assert response.message == "Success"
        assert response.data == {"result": "ok"}


class TestErrorResponse:
    """Tests for ErrorResponse schema."""
    
    def test_error_response_creation(self):
        """Test creating ErrorResponse."""
        response = ErrorResponse(
            message="Error occurred",
            error="ValidationError",
            details={"field": "email"}
        )
        assert response.success is False
        assert response.message == "Error occurred"
        assert response.error == "ValidationError"
        assert response.details == {"field": "email"}


class TestPaginatedResponse:
    """Tests for PaginatedResponse schema."""
    
    def test_paginated_response_creation(self):
        """Test creating PaginatedResponse."""
        response = PaginatedResponse(
            success=True,
            message="Items retrieved",
            data=[{"id": 1}, {"id": 2}],
            page=1,
            page_size=10,
            total=100,
            total_pages=10,
            has_next=True,
            has_previous=False
        )
        assert response.success is True
        assert len(response.data) == 2
        assert response.page == 1
        assert response.page_size == 10
        assert response.total == 100
        assert response.total_pages == 10
        assert response.has_next is True
        assert response.has_previous is False


class TestMessageResponse:
    """Tests for MessageResponse schema."""
    
    def test_message_response_creation(self):
        """Test creating MessageResponse."""
        response = MessageResponse(message="Operation completed")
        assert response.success is True
        assert response.message == "Operation completed"
        assert response.data is None


class TestFileUploadRequest:
    """Tests for FileUploadRequest schema."""
    
    def test_file_upload_request_creation(self):
        """Test creating FileUploadRequest."""
        request = FileUploadRequest(
            bucket_type="images",
            make_public=True,
            metadata={"key": "value"}
        )
        assert request.bucket_type == "images"
        assert request.make_public is True
        assert request.metadata == {"key": "value"}
    
    def test_file_upload_request_defaults(self):
        """Test FileUploadRequest defaults."""
        request = FileUploadRequest(bucket_type="documents")
        assert request.make_public is False
        assert request.metadata is None


class TestFileUploadResponse:
    """Tests for FileUploadResponse schema."""
    
    def test_file_upload_response_creation(self):
        """Test creating FileUploadResponse."""
        response = FileUploadResponse(
            message="File uploaded",
            data={
                "storage_path": "images/2024/01/test.jpg",
                "bucket_name": "images",
                "size": 1024
            }
        )
        assert response.success is True
        assert response.message == "File uploaded"
        assert response.data["storage_path"] == "images/2024/01/test.jpg"


class TestFileDownloadResponse:
    """Tests for FileDownloadResponse schema."""
    
    def test_file_download_response_creation(self):
        """Test creating FileDownloadResponse."""
        response = FileDownloadResponse(
            filename="test.jpg",
            content_type="image/jpeg",
            size=1024,
            content=b"file content"
        )
        assert response.filename == "test.jpg"
        assert response.content_type == "image/jpeg"
        assert response.size == 1024
        assert response.content == b"file content"


class TestFileInfo:
    """Tests for FileInfo schema."""
    
    def test_file_info_creation(self):
        """Test creating FileInfo."""
        file_info = FileInfo(
            id=1,
            filename="test.jpg",
            storage_path="images/2024/01/test.jpg",
            size=1024,
            content_type="image/jpeg",
            bucket_name="images",
            bucket_type="images",
            is_public=True,
            uploaded_by="user123",
            created_at="2024-01-01T00:00:00",
            url="https://example.com/test.jpg"
        )
        assert file_info.id == 1
        assert file_info.filename == "test.jpg"
        assert file_info.is_public is True
        assert file_info.url == "https://example.com/test.jpg"
    
    def test_file_info_optional_url(self):
        """Test FileInfo with optional URL."""
        file_info = FileInfo(
            id=1,
            filename="test.jpg",
            storage_path="path",
            size=1024,
            content_type="image/jpeg",
            bucket_name="images",
            bucket_type="images",
            is_public=False,
            uploaded_by="user123",
            created_at="2024-01-01T00:00:00"
        )
        assert file_info.url is None


class TestFileListResponse:
    """Tests for FileListResponse schema."""
    
    def test_file_list_response_creation(self):
        """Test creating FileListResponse."""
        files = [
            FileInfo(
                id=1,
                filename="test1.jpg",
                storage_path="path1",
                size=1024,
                content_type="image/jpeg",
                bucket_name="images",
                bucket_type="images",
                is_public=True,
                uploaded_by="user123",
                created_at="2024-01-01T00:00:00"
            )
        ]
        
        response = FileListResponse(
            success=True,
            message="Files retrieved",
            data=files,
            page=1,
            page_size=10,
            total=1,
            total_pages=1,
            has_next=False,
            has_previous=False
        )
        assert len(response.data) == 1
        assert response.page == 1


class TestFileDeleteResponse:
    """Tests for FileDeleteResponse schema."""
    
    def test_file_delete_response_creation(self):
        """Test creating FileDeleteResponse."""
        response = FileDeleteResponse(
            message="File deleted",
            data={
                "storage_path": "images/2024/01/test.jpg",
                "deleted": True
            }
        )
        assert response.success is True
        assert response.data["deleted"] is True

