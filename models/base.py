"""Base SQLModel class with common fields for all database models."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class BaseModel(SQLModel):
    """Base model class with common fields for all database entities."""
    
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Primary key identifier"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the record was created"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the record was last updated"
    )
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.utcnow()

