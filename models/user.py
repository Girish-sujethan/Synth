"""User model for authentication integration."""

from typing import Optional, Dict, Any
from sqlmodel import Field, Column, JSON
from models.base import BaseModel


class User(BaseModel, table=True):
    """
    User model for application users.
    
    This model extends BaseModel and integrates with Supabase authentication.
    The Supabase user ID is stored in the supabase_user_id field.
    """
    
    __tablename__ = "users"
    
    # Supabase user ID (from Supabase Auth)
    supabase_user_id: str = Field(
        unique=True,
        index=True,
        description="Supabase authentication user ID"
    )
    
    # User email (synced from Supabase)
    email: str = Field(
        unique=True,
        index=True,
        description="User email address"
    )
    
    # Optional user profile fields
    full_name: Optional[str] = Field(
        default=None,
        description="User's full name"
    )
    
    is_active: bool = Field(
        default=True,
        description="Whether the user account is active"
    )
    
    is_superuser: bool = Field(
        default=False,
        description="Whether the user has superuser privileges"
    )
    
    # Additional user metadata (JSON field for flexible storage)
    # Note: Using user_metadata to avoid conflict with SQLModel's metadata attribute
    user_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Additional user metadata"
    )

