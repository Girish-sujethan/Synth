"""Tasks router with risk assessment endpoints."""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Path, BackgroundTasks
from sqlalchemy.orm import Session

from db.session import get_session
from repositories.task import TaskRepository
from repositories.risk_assessment import TaskRiskAssessmentRepository
from services.edge_function import get_edge_function_service
from schemas.risk_assessment import (
    TaskCreate,
    TaskRead,
    AssessRisksResponse,
    RiskAssessmentResponse,
    AssessmentItem,
    RiskFactorSchema,
)
from core.exceptions import NotFoundError
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Creates a new task with the provided description and optional status."
)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_session)
) -> TaskRead:
    """
    Create a new task.
    
    Args:
        task_data: Task creation data (description and optional status)
        db: Database session
        
    Returns:
        TaskRead with created task data including ID and timestamps
    """
    task_repo = TaskRepository()
    
    # Create task
    task = task_repo.create(db, task_data.model_dump())
    
    logger.info(f"Created task {task.id}: {task.description}")
    
    return TaskRead(
        id=task.id,
        description=task.description,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get(
    "",
    response_model=List[TaskRead],
    status_code=status.HTTP_200_OK,
    summary="List all tasks",
    description="Retrieves a list of all tasks in the system."
)
async def list_tasks(
    db: Session = Depends(get_session)
) -> List[TaskRead]:
    """
    List all tasks.
    
    Args:
        db: Database session
        
    Returns:
        List of TaskRead objects
    """
    task_repo = TaskRepository()
    tasks = task_repo.find_all(db)
    
    return [
        TaskRead(
            id=task.id,
            description=task.description,
            status=task.status,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in tasks
    ]


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
    summary="Get a task by ID",
    description="Retrieves a single task by its ID."
)
async def get_task(
    task_id: int = Path(..., description="Task ID", gt=0),
    db: Session = Depends(get_session)
) -> TaskRead:
    """
    Get a task by ID.
    
    Args:
        task_id: Task ID
        db: Database session
        
    Returns:
        TaskRead with task data
        
    Raises:
        HTTPException: 404 if task not found
    """
    task_repo = TaskRepository()
    task = task_repo.get_by_id(db, task_id)
    
    if not task:
        raise NotFoundError(resource="Task", identifier=str(task_id))
    
    return TaskRead(
        id=task.id,
        description=task.description,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.post(
    "/{task_id}/assess-risks",
    response_model=AssessRisksResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger risk assessment for a task",
    description="Initiates risk assessment for a task's decomposition. Returns immediately with acceptance status."
)
async def assess_task_risks(
    task_id: int = Path(..., description="Task ID to assess", gt=0),
    db: Session = Depends(get_session),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> AssessRisksResponse:
    """
    Trigger risk assessment for a task.
    
    This endpoint initiates the risk assessment process for a task.
    The actual assessment processing happens asynchronously.
    
    Args:
        task_id: Task ID to assess
        db: Database session
        
    Returns:
        AssessRisksResponse with task_id and status
        
    Raises:
        HTTPException: 404 if task not found
    """
    task_repo = TaskRepository()
    task = task_repo.get_by_id(db, task_id)
    
    if not task:
        raise NotFoundError(resource="Task", identifier=str(task_id))
    
    # Trigger risk assessment via Supabase Edge Function in background
    # Note: In a real implementation, you would get subtasks and dependencies
    # from the task decomposition. For now, we'll trigger the function
    # and let it handle the assessment asynchronously.
    def invoke_assessment():
        """Background task to invoke Edge Function."""
        try:
            edge_function_service = get_edge_function_service()
            
            # Prepare payload for Edge Function
            # In production, this would include actual subtasks and dependencies
            payload = {
                "task_id": task_id,
                "subtasks": [],  # TODO: Get from task decomposition
                "dependencies": [],  # TODO: Get from dependency graph
            }
            
            # Invoke Edge Function
            result = edge_function_service.invoke_function("assess-risks", payload)
            logger.info(f"Risk assessment completed for task {task_id}: {result}")
        except Exception as e:
            logger.error(f"Failed to invoke risk assessment Edge Function for task {task_id}: {str(e)}")
    
    # Add background task
    background_tasks.add_task(invoke_assessment)
    
    logger.info(f"Risk assessment triggered for task {task_id} via Edge Function")
    
    return AssessRisksResponse(
        task_id=task_id,
        status="assessing_risks"
    )


@router.get(
    "/{task_id}/risk-assessment",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get risk assessment results for a task",
    description="Retrieves complete risk assessment data for a task, including all subtask assessments."
)
async def get_task_risk_assessment(
    task_id: int = Path(..., description="Task ID to get assessment for", gt=0),
    db: Session = Depends(get_session)
) -> RiskAssessmentResponse:
    """
    Get risk assessment results for a task.
    
    Retrieves all risk assessments associated with a task, including
    assessments for subtasks.
    
    Args:
        task_id: Task ID to get assessment for
        db: Database session
        
    Returns:
        RiskAssessmentResponse with task_id, assessments array, and created_at
        
    Raises:
        HTTPException: 404 if task not found or no assessments exist
    """
    task_repo = TaskRepository()
    assessment_repo = TaskRiskAssessmentRepository()
    
    # Verify task exists
    task = task_repo.get_by_id(db, task_id)
    if not task:
        raise NotFoundError(resource="Task", identifier=str(task_id))
    
    # Get all assessments for this task
    assessments = assessment_repo.get_by_task_id(db, task_id)
    
    if not assessments:
        raise NotFoundError(
            resource="Risk assessment",
            identifier=f"task_id={task_id}"
        )
    
    # Convert to response format
    assessment_items: List[AssessmentItem] = []
    earliest_created_at: datetime = assessments[0].created_at
    
    for assessment in assessments:
        # Track earliest creation time
        if assessment.created_at < earliest_created_at:
            earliest_created_at = assessment.created_at
        
        # Convert risk_factors from dict/list to RiskFactorSchema objects
        risk_factors = None
        if assessment.risk_factors:
            try:
                risk_factors = [
                    RiskFactorSchema(**factor) if isinstance(factor, dict) else factor
                    for factor in assessment.risk_factors
                ]
            except Exception as e:
                logger.warning(f"Error parsing risk factors for assessment {assessment.id}: {e}")
                risk_factors = None
        
        assessment_items.append(
            AssessmentItem(
                id=assessment.id,
                subtask_id=assessment.subtask_id,
                risk_level=assessment.risk_level,
                risk_factors=risk_factors,
                mitigation_suggestions=assessment.mitigation_suggestions,
            )
        )
    
    return RiskAssessmentResponse(
        task_id=task_id,
        assessments=assessment_items,
        created_at=earliest_created_at
    )

