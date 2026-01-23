"""Storage configuration with bucket settings, file size limits, and allowed file types."""

from typing import List, Dict
from pathlib import Path


class StorageConfig:
    """Configuration for Supabase Storage operations."""
    
    # Default bucket names
    DEFAULT_BUCKETS = {
        "artifacts": "artifacts",
        "documents": "documents",
        "images": "images",
    }
    
    # File size limits (in bytes)
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
    MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10 MB
    MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50 MB
    MAX_ARTIFACT_SIZE = 100 * 1024 * 1024  # 100 MB
    
    # Allowed file types by category
    ALLOWED_IMAGE_TYPES = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
    ]
    
    ALLOWED_DOCUMENT_TYPES = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "text/plain",
        "text/csv",
    ]
    
    ALLOWED_ARTIFACT_TYPES = [
        "application/zip",
        "application/x-tar",
        "application/gzip",
        "application/json",
        "application/xml",
        "text/plain",
    ]
    
    # File organization settings
    FOLDER_STRUCTURE = {
        "images": "images/{year}/{month}",
        "documents": "documents/{year}/{month}",
        "artifacts": "artifacts/{year}/{month}",
    }
    
    # Public vs private buckets
    PUBLIC_BUCKETS = ["images"]  # Buckets that allow public access
    PRIVATE_BUCKETS = ["documents", "artifacts"]  # Buckets requiring authentication
    
    @classmethod
    def get_allowed_types(cls, bucket_type: str) -> List[str]:
        """
        Get allowed file types for a bucket type.
        
        Args:
            bucket_type: Type of bucket (images, documents, artifacts)
            
        Returns:
            List of allowed MIME types
        """
        type_map = {
            "images": cls.ALLOWED_IMAGE_TYPES,
            "documents": cls.ALLOWED_DOCUMENT_TYPES,
            "artifacts": cls.ALLOWED_ARTIFACT_TYPES,
        }
        return type_map.get(bucket_type, [])
    
    @classmethod
    def get_max_size(cls, bucket_type: str) -> int:
        """
        Get maximum file size for a bucket type.
        
        Args:
            bucket_type: Type of bucket (images, documents, artifacts)
            
        Returns:
            Maximum file size in bytes
        """
        size_map = {
            "images": cls.MAX_IMAGE_SIZE,
            "documents": cls.MAX_DOCUMENT_SIZE,
            "artifacts": cls.MAX_ARTIFACT_SIZE,
        }
        return size_map.get(bucket_type, cls.MAX_FILE_SIZE)
    
    @classmethod
    def is_public_bucket(cls, bucket_name: str) -> bool:
        """
        Check if a bucket is public.
        
        Args:
            bucket_name: Name of the bucket
            
        Returns:
            True if bucket is public, False otherwise
        """
        return bucket_name in cls.PUBLIC_BUCKETS

