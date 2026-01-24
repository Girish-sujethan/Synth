"""Task model for database representation of tasks."""

from typing import Optional
from sqlmodel import Field
from models.base import BaseModel


class Task(BaseModel, table=True):
    """
    Task model for storing task information.
    
    This model serves as the parent table for task risk assessments.
    """
    
    __tablename__ = "tasks"
    
    # Task description
    description: str = Field(
        description="Task description"
    )
    
    # Task status
    status: Optional[str] = Field(
        default="pending",
        description="Task status (e.g., pending, in_progress, completed)"
    )

