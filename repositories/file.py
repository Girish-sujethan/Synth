"""FileRepository for database operations related to file metadata."""

from typing import Optional, List
from sqlalchemy.orm import Session

from models.file import File
from repositories.base import BaseRepository


class FileRepository(BaseRepository[File]):
    """
    Repository for File model with file-specific operations.
    """
    
    def __init__(self):
        super().__init__(File)
    
    def get_by_storage_path(
        self,
        db: Session,
        storage_path: str
    ) -> Optional[File]:
        """
        Get file by storage path.
        
        Args:
            db: Database session
            storage_path: Path in Supabase Storage
            
        Returns:
            File instance or None if not found
        """
        return self.get_by_field(db, "storage_path", storage_path)
    
    def get_by_hash(
        self,
        db: Session,
        file_hash: str
    ) -> Optional[File]:
        """
        Get file by content hash.
        
        Args:
            db: Database session
            file_hash: SHA-256 hash of file content
            
        Returns:
            File instance or None if not found
        """
        return self.get_by_field(db, "file_hash", file_hash)
    
    def get_by_user(
        self,
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        """
        Get files uploaded by a user.
        
        Args:
            db: Database session
            user_id: Supabase user ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of File instances
        """
        return self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"uploaded_by": user_id}
        )
    
    def get_by_bucket(
        self,
        db: Session,
        bucket_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        """
        Get files in a specific bucket.
        
        Args:
            db: Database session
            bucket_name: Bucket name
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of File instances
        """
        return self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"bucket_name": bucket_name}
        )
    
    def get_public_files(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        """
        Get all public files.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of public File instances
        """
        return self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"is_public": True}
        )

