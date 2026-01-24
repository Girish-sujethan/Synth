"""TaskRepository with task-related database operations."""

from typing import Optional
from sqlalchemy.orm import Session

from models.task import Task
from repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """
    Repository for Task model with task-specific operations.
    """
    
    def __init__(self):
        super().__init__(Task)
    
    def get_by_id(
        self,
        db: Session,
        task_id: int
    ) -> Optional[Task]:
        """
        Get task by ID.
        
        Args:
            db: Database session
            task_id: Task ID
            
        Returns:
            Task instance or None if not found
        """
        return self.get(db, task_id)

