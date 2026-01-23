"""Storage utilities for file validation, path generation, and metadata extraction."""

import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from config.storage import StorageConfig


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension (without dot)
    """
    return Path(filename).suffix.lstrip('.').lower()


def get_mime_type(filename: str) -> str:
    """
    Get MIME type for a file.
    
    Args:
        filename: Name of the file
        
    Returns:
        MIME type string
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


def validate_file_type(
    filename: str,
    bucket_type: str,
    content_type: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate if a file type is allowed for a bucket.
    
    Args:
        filename: Name of the file
        bucket_type: Type of bucket (images, documents, artifacts)
        content_type: Optional MIME type to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    allowed_types = StorageConfig.get_allowed_types(bucket_type)
    
    # Use provided content_type or guess from filename
    mime_type = content_type or get_mime_type(filename)
    
    if mime_type not in allowed_types:
        return False, f"File type {mime_type} is not allowed for {bucket_type} bucket"
    
    return True, None


def validate_file_size(file_size: int, bucket_type: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if file size is within limits.
    
    Args:
        file_size: Size of the file in bytes
        bucket_type: Type of bucket (images, documents, artifacts)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    max_size = StorageConfig.get_max_size(bucket_type)
    
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        file_size_mb = file_size / (1024 * 1024)
        return False, f"File size {file_size_mb:.2f} MB exceeds maximum {max_size_mb:.2f} MB"
    
    if file_size == 0:
        return False, "File cannot be empty"
    
    return True, None


def generate_storage_path(
    filename: str,
    bucket_type: str,
    user_id: Optional[str] = None
) -> str:
    """
    Generate storage path for a file.
    
    Args:
        filename: Original filename
        bucket_type: Type of bucket (images, documents, artifacts)
        user_id: Optional user ID for user-specific paths
        
    Returns:
        Storage path string
    """
    now = datetime.utcnow()
    folder_template = StorageConfig.FOLDER_STRUCTURE.get(
        bucket_type,
        f"{bucket_type}/{{year}}/{{month}}"
    )
    
    folder = folder_template.format(
        year=now.year,
        month=f"{now.month:02d}"
    )
    
    # Add user-specific folder if provided
    if user_id:
        folder = f"{folder}/{user_id}"
    
    # Generate unique filename with timestamp
    file_stem = Path(filename).stem
    file_ext = get_file_extension(filename)
    timestamp = int(now.timestamp())
    
    # Create unique filename
    unique_filename = f"{file_stem}_{timestamp}.{file_ext}"
    
    return f"{folder}/{unique_filename}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove unsafe characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = Path(filename).name
    
    # Replace unsafe characters
    unsafe_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        stem = Path(filename).stem[:200]
        ext = Path(filename).suffix
        filename = f"{stem}{ext}"
    
    return filename


def calculate_file_hash(file_content: bytes) -> str:
    """
    Calculate SHA-256 hash of file content.
    
    Args:
        file_content: File content as bytes
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(file_content).hexdigest()


def extract_file_metadata(
    filename: str,
    file_size: int,
    content_type: Optional[str] = None
) -> dict:
    """
    Extract metadata from a file.
    
    Args:
        filename: Name of the file
        file_size: Size of the file in bytes
        content_type: Optional MIME type
        
    Returns:
        Dictionary with file metadata
    """
    mime_type = content_type or get_mime_type(filename)
    extension = get_file_extension(filename)
    
    return {
        "filename": filename,
        "size": file_size,
        "content_type": mime_type,
        "extension": extension,
        "uploaded_at": datetime.utcnow().isoformat(),
    }

