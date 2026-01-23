"""File model for database representation of file metadata."""

from typing import Optional
from sqlmodel import Field, Column, JSON
from models.base import BaseModel


class File(BaseModel, table=True):
    """
    File model for tracking file metadata in the database.
    
    This model stores metadata about files uploaded to Supabase Storage,
    including their location, size, type, and ownership.
    """
    
    __tablename__ = "files"
    
    # File identification
    filename: str = Field(
        description="Original filename"
    )
    
    storage_path: str = Field(
        unique=True,
        index=True,
        description="Path in Supabase Storage"
    )
    
    # File metadata
    size: int = Field(
        description="File size in bytes"
    )
    
    content_type: str = Field(
        description="MIME type of the file"
    )
    
    file_hash: Optional[str] = Field(
        default=None,
        index=True,
        description="SHA-256 hash of file content for deduplication"
    )
    
    # Bucket information
    bucket_name: str = Field(
        index=True,
        description="Supabase Storage bucket name"
    )
    
    bucket_type: str = Field(
        index=True,
        description="Type of bucket (images, documents, artifacts)"
    )
    
    # Ownership and access
    uploaded_by: Optional[str] = Field(
        default=None,
        index=True,
        description="Supabase user ID of the uploader"
    )
    
    is_public: bool = Field(
        default=False,
        description="Whether the file is publicly accessible"
    )
    
    # Additional metadata (JSON field for flexible storage)
    # Note: Using file_metadata to avoid conflict with SQLModel's metadata attribute
    file_metadata: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Additional file metadata"
    )

