"""Pydantic schemas for file upload/download requests and responses."""

from typing import Optional, List
from pydantic import BaseModel, Field
from schemas.common import SuccessResponse, PaginatedResponse


class FileUploadRequest(BaseModel):
    """Request schema for file upload."""
    
    bucket_type: str = Field(
        description="Type of bucket (images, documents, artifacts)",
        examples=["images", "documents", "artifacts"]
    )
    
    make_public: bool = Field(
        default=False,
        description="Whether to make the file publicly accessible"
    )
    
    metadata: Optional[dict] = Field(
        default=None,
        description="Additional metadata to store with the file"
    )


class FileUploadResponse(SuccessResponse[dict]):
    """Response schema for file upload."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "File uploaded successfully",
                "data": {
                    "storage_path": "images/2024/01/user123/image_1234567890.jpg",
                    "bucket_name": "images",
                    "bucket_type": "images",
                    "filename": "image.jpg",
                    "size": 102400,
                    "content_type": "image/jpeg",
                    "file_hash": "abc123...",
                    "is_public": True,
                }
            }
        }


class FileDownloadResponse(BaseModel):
    """Response schema for file download."""
    
    filename: str = Field(description="Original filename")
    content_type: str = Field(description="MIME type of the file")
    size: int = Field(description="File size in bytes")
    content: bytes = Field(description="File content")


class FileInfo(BaseModel):
    """File information schema."""
    
    id: int = Field(description="File ID")
    filename: str = Field(description="Original filename")
    storage_path: str = Field(description="Path in Supabase Storage")
    size: int = Field(description="File size in bytes")
    content_type: str = Field(description="MIME type")
    bucket_name: str = Field(description="Bucket name")
    bucket_type: str = Field(description="Bucket type")
    is_public: bool = Field(description="Whether file is public")
    uploaded_by: Optional[str] = Field(description="User ID of uploader")
    created_at: str = Field(description="Upload timestamp")
    url: Optional[str] = Field(default=None, description="Public or signed URL")


class FileListResponse(PaginatedResponse[FileInfo]):
    """Response schema for file list."""
    
    pass


class FileDeleteResponse(SuccessResponse[dict]):
    """Response schema for file deletion."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "File deleted successfully",
                "data": {
                    "storage_path": "images/2024/01/user123/image_1234567890.jpg",
                    "deleted": True
                }
            }
        }

