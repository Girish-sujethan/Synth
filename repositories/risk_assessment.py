"""TaskRiskAssessmentRepository with risk assessment database operations."""

from typing import Optional, List
from sqlalchemy.orm import Session

from models.risk_assessment import TaskRiskAssessment
from repositories.base import BaseRepository


class TaskRiskAssessmentRepository(BaseRepository[TaskRiskAssessment]):
    """
    Repository for TaskRiskAssessment model with risk assessment-specific operations.
    """
    
    def __init__(self):
        super().__init__(TaskRiskAssessment)
    
    def get_by_task_id(
        self,
        db: Session,
        task_id: int
    ) -> List[TaskRiskAssessment]:
        """
        Get all risk assessments for a specific task.
        
        Args:
            db: Database session
            task_id: Task ID
            
        Returns:
            List of TaskRiskAssessment instances for the task
        """
        return self.find_by(db, task_id=task_id)
    
    def get_by_task_and_subtask(
        self,
        db: Session,
        task_id: int,
        subtask_id: str
    ) -> Optional[TaskRiskAssessment]:
        """
        Get risk assessment for a specific task and subtask.
        
        Args:
            db: Database session
            task_id: Task ID
            subtask_id: Subtask identifier
            
        Returns:
            TaskRiskAssessment instance or None if not found
        """
        return self.find_one_by(db, task_id=task_id, subtask_id=subtask_id)

