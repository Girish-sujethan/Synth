"""UserRepository with specific user-related database operations."""

from typing import Optional
from sqlalchemy.orm import Session

from models.user import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for User model with user-specific operations.
    """
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_supabase_id(
        self,
        db: Session,
        supabase_user_id: str
    ) -> Optional[User]:
        """
        Get user by Supabase user ID.
        
        Args:
            db: Database session
            supabase_user_id: Supabase authentication user ID
            
        Returns:
            User instance or None if not found
        """
        return self.get_by_field(db, "supabase_user_id", supabase_user_id)
    
    def get_by_email(
        self,
        db: Session,
        email: str
    ) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            db: Database session
            email: User email address
            
        Returns:
            User instance or None if not found
        """
        return self.get_by_field(db, "email", email)
    
    def create_or_update_from_supabase(
        self,
        db: Session,
        supabase_user_id: str,
        email: str,
        **kwargs
    ) -> User:
        """
        Create or update user from Supabase authentication data.
        
        Args:
            db: Database session
            supabase_user_id: Supabase user ID
            email: User email
            **kwargs: Additional user attributes
            
        Returns:
            User instance
        """
        user = self.get_by_supabase_id(db, supabase_user_id)
        
        if user:
            # Update existing user
            update_data = {"email": email, **kwargs}
            return self.update(db, user, update_data)
        else:
            # Create new user
            user_data = {
                "supabase_user_id": supabase_user_id,
                "email": email,
                **kwargs
            }
            return self.create(db, user_data)
    
    def deactivate(self, db: Session, user_id: int) -> Optional[User]:
        """
        Deactivate a user account.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Updated User instance or None if not found
        """
        user = self.get(db, user_id)
        if user:
            return self.update(db, user, {"is_active": False})
        return None
    
    def activate(self, db: Session, user_id: int) -> Optional[User]:
        """
        Activate a user account.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Updated User instance or None if not found
        """
        user = self.get(db, user_id)
        if user:
            return self.update(db, user, {"is_active": True})
        return None

