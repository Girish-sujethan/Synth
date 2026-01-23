"""StorageService class with methods for upload, download, delete, and list operations using Supabase Storage."""

from typing import Optional, List, BinaryIO
from pathlib import Path
from supabase import create_client, Client
from config import settings
from config.storage import StorageConfig
from core.storage import (
    validate_file_type,
    validate_file_size,
    generate_storage_path,
    sanitize_filename,
    calculate_file_hash,
    extract_file_metadata,
)
from core.logging import get_logger

logger = get_logger(__name__)


class StorageService:
    """
    Service for Supabase Storage operations.
    
    Handles file upload, download, delete, and list operations
    with proper validation and error handling.
    """
    
    def __init__(self):
        """Initialize Supabase Storage client."""
        if not settings.supabase_url:
            raise ValueError("SUPABASE_URL is not configured")
        
        supabase_key = settings.supabase_key or ""
        self.supabase: Client = create_client(settings.supabase_url, supabase_key)
        self.storage = self.supabase.storage
    
    def upload_file(
        self,
        file_content: bytes,
        filename: str,
        bucket_type: str,
        user_id: Optional[str] = None,
        content_type: Optional[str] = None,
        make_public: bool = False
    ) -> dict:
        """
        Upload a file to Supabase Storage.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            bucket_type: Type of bucket (images, documents, artifacts)
            user_id: Optional user ID for ownership
            content_type: Optional MIME type
            make_public: Whether to make the file publicly accessible
            
        Returns:
            Dictionary with upload result including storage_path and metadata
            
        Raises:
            ValueError: If file validation fails
            Exception: If upload fails
        """
        # Validate file
        is_valid, error = validate_file_type(filename, bucket_type, content_type)
        if not is_valid:
            raise ValueError(error)
        
        is_valid, error = validate_file_size(len(file_content), bucket_type)
        if not is_valid:
            raise ValueError(error)
        
        # Get bucket name
        bucket_name = StorageConfig.DEFAULT_BUCKETS.get(bucket_type, bucket_type)
        
        # Generate storage path
        sanitized_filename = sanitize_filename(filename)
        storage_path = generate_storage_path(sanitized_filename, bucket_type, user_id)
        
        # Calculate file hash
        file_hash = calculate_file_hash(file_content)
        
        # Upload to Supabase Storage
        try:
            response = self.storage.from_(bucket_name).upload(
                path=storage_path,
                file=file_content,
                file_options={
                    "content-type": content_type or "application/octet-stream",
                    "upsert": False,  # Don't overwrite existing files
                }
            )
            
            # Make public if requested and bucket supports it
            if make_public and StorageConfig.is_public_bucket(bucket_name):
                self.storage.from_(bucket_name).make_public(storage_path)
            
            # Extract metadata
            metadata = extract_file_metadata(
                sanitized_filename,
                len(file_content),
                content_type
            )
            
            return {
                "storage_path": storage_path,
                "bucket_name": bucket_name,
                "bucket_type": bucket_type,
                "filename": sanitized_filename,
                "size": len(file_content),
                "content_type": content_type or metadata["content_type"],
                "file_hash": file_hash,
                "is_public": make_public and StorageConfig.is_public_bucket(bucket_name),
                "metadata": metadata,
            }
            
        except Exception as e:
            logger.error(f"Failed to upload file {filename}: {str(e)}")
            raise Exception(f"File upload failed: {str(e)}")
    
    def download_file(
        self,
        storage_path: str,
        bucket_name: str
    ) -> bytes:
        """
        Download a file from Supabase Storage.
        
        Args:
            storage_path: Path to the file in storage
            bucket_name: Name of the bucket
            
        Returns:
            File content as bytes
            
        Raises:
            Exception: If download fails
        """
        try:
            response = self.storage.from_(bucket_name).download(storage_path)
            return response
        except Exception as e:
            logger.error(f"Failed to download file {storage_path}: {str(e)}")
            raise Exception(f"File download failed: {str(e)}")
    
    def delete_file(
        self,
        storage_path: str,
        bucket_name: str
    ) -> bool:
        """
        Delete a file from Supabase Storage.
        
        Args:
            storage_path: Path to the file in storage
            bucket_name: Name of the bucket
            
        Returns:
            True if deletion was successful
            
        Raises:
            Exception: If deletion fails
        """
        try:
            response = self.storage.from_(bucket_name).remove([storage_path])
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {storage_path}: {str(e)}")
            raise Exception(f"File deletion failed: {str(e)}")
    
    def list_files(
        self,
        bucket_name: str,
        folder_path: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """
        List files in a bucket.
        
        Args:
            bucket_name: Name of the bucket
            folder_path: Optional folder path to list
            limit: Maximum number of files to return
            
        Returns:
            List of file information dictionaries
        """
        try:
            response = self.storage.from_(bucket_name).list(
                path=folder_path or "",
                limit=limit
            )
            return response or []
        except Exception as e:
            logger.error(f"Failed to list files in {bucket_name}: {str(e)}")
            return []
    
    def get_public_url(
        self,
        storage_path: str,
        bucket_name: str
    ) -> str:
        """
        Get public URL for a file.
        
        Args:
            storage_path: Path to the file in storage
            bucket_name: Name of the bucket
            
        Returns:
            Public URL string
        """
        try:
            response = self.storage.from_(bucket_name).get_public_url(storage_path)
            return response
        except Exception as e:
            logger.error(f"Failed to get public URL for {storage_path}: {str(e)}")
            raise Exception(f"Failed to get public URL: {str(e)}")
    
    def get_signed_url(
        self,
        storage_path: str,
        bucket_name: str,
        expires_in: int = 3600
    ) -> str:
        """
        Get signed URL for a file (temporary access).
        
        Args:
            storage_path: Path to the file in storage
            bucket_name: Name of the bucket
            expires_in: Expiration time in seconds (default: 1 hour)
            
        Returns:
            Signed URL string
        """
        try:
            response = self.storage.from_(bucket_name).create_signed_url(
                path=storage_path,
                expires_in=expires_in
            )
            return response.get("signedURL", "")
        except Exception as e:
            logger.error(f"Failed to get signed URL for {storage_path}: {str(e)}")
            raise Exception(f"Failed to get signed URL: {str(e)}")

