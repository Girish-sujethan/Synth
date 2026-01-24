"""Task management API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status

from backend.app.core.middleware import get_current_user, require_team_membership
from backend.app.schemas.auth import TokenData
from backend.app.schemas.tasks import (
    TaskCreateRequest,
    TaskDetailResponse,
    TaskMoveRequest,
    TaskMoveResponse,
    TaskResponse,
    TaskSplitConfirmRequest,
    TaskSplitConfirmResponse,
    TaskSplitPreviewResponse,
    TaskSplitRequest,
    TaskUpdateRequest,
)
from backend.app.services.task_service import TaskService
from backend.app.services.task_split_service import TaskSplitService
from backend.app.services.task_approval_service import TaskApprovalService
from backend.app.services.column_service import ColumnService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
async def create_task(
    request: TaskCreateRequest,
    team_id: UUID = Query(..., description="Team ID"),
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> TaskResponse:
    """
    Create a new task.

    Requires:
    - Authentication (JWT token)
    - Team membership
    - Valid task data (title non-empty, size Fibonacci, etc.)
    """
    return await TaskService.create_task(team_id, request, user)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    team_id: UUID = Query(..., description="Team ID"),
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> TaskResponse:
    """
    Get a task by ID.

    Requires:
    - Authentication (JWT token)
    - Team membership
    """
    return await TaskService.get_task(task_id, team_id, user)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    team_id: UUID,
    request: TaskUpdateRequest,
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> TaskResponse:
    """
    Update a task.

    Requires:
    - Authentication (JWT token)
    - Team membership
    - Permission: task creator, admin, or manager
    """
    return await TaskService.update_task(task_id, team_id, request, user)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    team_id: UUID = Query(..., description="Team ID"),
    cascade: bool = Query(False, description="If true, delete task and all subtasks. If false, block deletion if task has subtasks."),
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> None:
    """
    Delete a task.

    If the task has subtasks:
    - cascade=false (default): Returns error, deletion blocked
    - cascade=true: Deletes task and all subtasks (CASCADE)

    Requires:
    - Authentication (JWT token)
    - Team membership
    - Permission: admin or manager only
    """
    await TaskService.delete_task(task_id, team_id, user, cascade=cascade)


@router.post("/{task_id}/move", response_model=TaskMoveResponse)
async def move_task(
    task_id: UUID = Path(..., description="Task ID"),
    request: TaskMoveRequest = ...,
    team_id: UUID = Query(..., description="Team ID"),
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> TaskMoveResponse:
    """
    Move a task to a different column.

    Enforces WIP limits and AI review gating rules.

    Requires:
    - Authentication (JWT token)
    - Team membership
    """
    result = await ColumnService.move_task(
        team_id=team_id,
        task_id=task_id,
        column_key=request.column_key,
        user=user,
        note=request.note,
        client_action=request.client_action,
    )
    return TaskMoveResponse(**result)


@router.post("/{task_id}/split", response_model=TaskSplitPreviewResponse)
async def split_task_preview(
    task_id: UUID = Path(..., description="Task ID"),
    request: TaskSplitRequest = ...,
    team_id: UUID = Query(..., description="Team ID"),
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> TaskSplitPreviewResponse:
    """
    Generate a preview of subtasks for a task split using LLM.

    This endpoint does not persist subtasks to the database. Use the confirm-split
    endpoint to create the subtasks.

    Requires:
    - Authentication (JWT token)
    - Team membership
    """
    service = TaskSplitService()
    result = await service.split_task_preview(
        task_id=task_id,
        team_id=team_id,
        instructions=request.instructions,
        policy_version=request.policy_version,
    )
    # Convert subtasks dict to SubtaskPreview objects
    from backend.app.schemas.tasks import SubtaskPreview
    subtask_previews = [SubtaskPreview(**st) for st in result["subtasks"]]
    return TaskSplitPreviewResponse(
        subtasks=subtask_previews,
        policy_version=result["policy_version"],
        model=result["model"],
        parent_task_id=result["parent_task_id"],
    )


@router.post("/{task_id}/split/confirm", response_model=TaskSplitConfirmResponse)
async def confirm_task_split(
    task_id: UUID = Path(..., description="Task ID"),
    request: TaskSplitConfirmRequest = ...,
    team_id: UUID = Query(..., description="Team ID"),
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> TaskSplitConfirmResponse:
    """
    Confirm and persist subtasks from a task split.

    The subtasks in the request may have been edited by the user after the preview.
    All validation rules are applied before persistence.

    Requires:
    - Authentication (JWT token)
    - Team membership
    - Admin or Manager role
    """
    # Check if user has admin or manager role
    from backend.app.db.queries import get_user_role_in_team
    from backend.app.core.exceptions import AuthorizationError
    from backend.app.schemas.auth import UserRole

    user_role = await get_user_role_in_team(team_id, user.user_id)
    if user_role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise AuthorizationError(
            "Only admins and managers can confirm task splits",
            details={"required_roles": ["admin", "manager"], "user_role": user_role.value if user_role else None},
        )

    # Validate at least one subtask
    if not request.subtasks:
        from backend.app.core.exceptions import APIException
        raise APIException(
            code="INVALID_SUBTASK_DATA",
            message="At least one subtask is required",
            status_code=400,
        )

    service = TaskSplitService()
    # Convert SubtaskPreview to dict for service
    subtasks_dict = [st.model_dump() for st in request.subtasks]
    result = await service.confirm_split(
        task_id=task_id,
        team_id=team_id,
        subtasks=subtasks_dict,
        user=user,
    )
    # Convert UUID strings to UUID objects
    from uuid import UUID as UUIDType
    return TaskSplitConfirmResponse(
        parent_task_id=UUIDType(result["parent_task_id"]),
        subtask_ids=[UUIDType(sid) for sid in result["subtask_ids"]],
        subtask_count=result["subtask_count"],
        policy_version=result["policy_version"],
        model=result["model"],
    )
d}/orchestrate/preview", response_model=TaskOrchestrationPreviewResponse)
async def orchestrate_task_preview(
    task_id: UUID = Path(..., description="Task ID"),
    request: TaskOrchestrateRequest = ...,
    team_id: UUID = Query(..., description="Team ID"),
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> TaskOrchestrationPreviewResponse:
    """
    Generate a preview of task assignments for orchestration using LLM.

    This endpoint does not persist assignments to the database. Use the confirm endpoint
    to apply the assignments.

    Requires:
    - Authentication (JWT token)
    - Team membership
    """
    service = TaskOrchestrationService()
    result = await service.orchestrate_preview(
        task_id=task_id,
        team_id=team_id,
        strategy=request.strategy or "balanced",
        instructions=request.instructions,
    )
    # Convert assignments dict to AssignmentPreview objects
    from backend.app.schemas.tasks import AssignmentPreview
    assignment_previews = [AssignmentPreview(**a) for a in result["assignments"]]
    return TaskOrchestrationPreviewResponse(
        assignments=assignment_previews,
        policy_version=result["policy_version"],
        model=result["model"],
        parent_task_id=result["parent_task_id"],
    )


@router.post("/{task_id}/orchestrate/confirm", response_model=TaskOrchestrationConfirmResponse)
async def confirm_task_orchestration(
    task_id: UUID = Path(..., description="Task ID"),
    request: TaskOrchestrationConfirmRequest = ...,
    team_id: UUID = Query(..., description="Team ID"),
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> TaskOrchestrationConfirmResponse:
    """
    Confirm and persist task assignments from orchestration.

    The assignments in the request may have been edited by the user after the preview.
    All validation rules are applied before persistence.

    Requires:
    - Authentication (JWT token)
    - Team membership
    - Admin or Manager role
    """
    # Check if user has admin or manager role
    from backend.app.db.queries import get_user_role_in_team
    from backend.app.core.exceptions import AuthorizationError
    from backend.app.schemas.auth import UserRole

    user_role = await get_user_role_in_team(team_id, user.user_id)
    if user_role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise AuthorizationError(
            "Only admins and managers can confirm task orchestration",
            details={"required_roles": ["admin", "manager"], "user_role": user_role.value if user_role else None},
        )

    # Validate at least one assignment
    if not request.assignments:
        from backend.app.core.exceptions import APIException
        raise APIException(
            code="INVALID_ASSIGNMENT_DATA",
            message="At least one assignment is required",
            status_code=400,
        )

    service = TaskOrchestrationService()
    # Convert AssignmentPreview to dict for service
    assignments_dict = [a.model_dump() for a in request.assignments]
    result = await service.confirm_orchestration(
        task_id=task_id,
        team_id=team_id,
        assignments=assignments_dict,
        user=user,
    )
    # Convert assignment results
    from backend.app.schemas.tasks import AssignmentResult
    from uuid import UUID as UUIDType
    assignment_results = [
        AssignmentResult(
            subtask_id=UUIDType(a["subtask_id"]),
            assignee_type=a["assignee_type"],
            assignee_id=UUIDType(a["assignee_id"]),
            assignment_risk=a["assignment_risk"],
        )
        for a in result["assignments"]
    ]
    return TaskOrchestrationConfirmResponse(
        parent_task_id=UUIDType(result["parent_task_id"]),
        assignments=assignment_results,
        assignment_count=result["assignment_count"],
        policy_version=result["policy_version"],
        model=result["model"],
    )


@router.post("/{task_id}/approve", response_model=TaskApprovalResponse)
async def approve_task(
    task_id: UUID = Path(..., description="Task ID"),
    request: TaskApprovalRequest = ...,
    team_id: UUID = Query(..., description="Team ID"),
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> TaskApprovalResponse:
    """
    Approve or reject an AI-assigned task.

    This endpoint allows human reviewers to approve or reject tasks that are
    AI-assigned or have approval-required tags. Approved tasks can bypass
    review gating when moving to done.

    Requires:
    - Authentication (JWT token)
    - Team membership
    """
    service = TaskApprovalService()
    result = await service.approve_task(
        task_id=task_id,
        team_id=team_id,
        approved=request.approved,
        user=user,
        comment=request.comment,
    )
    from datetime import datetime
    from uuid import UUID as UUIDType
    return TaskApprovalResponse(
        task_id=UUIDType(result["task_id"]),
        approved=result["approved"],
        approved_at=datetime.fromisoformat(result["approved_at"]) if result.get("approved_at") else None,
        approved_by=result.get("approved_by"),
        comment=result.get("comment"),
    )


@router.post("/{task_id}/run-agent", status_code=status.HTTP_202_ACCEPTED)
async def run_agent(
    task_id: UUID = Path(..., description="Task ID"),
    team_id: UUID = Query(..., description="Team ID"),
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> dict:
    """
    Initiate AI agent execution for an AI-assigned task.

    This endpoint triggers the AI agent to start working on the task.
    The actual execution happens asynchronously. This endpoint only
    initiates the process and returns immediately.

    Requires:
    - Authentication (JWT token)
    - Team membership
    - Task must be AI-assigned
    """
    from backend.app.db.queries import get_task, create_event
    from backend.app.core.exceptions import APIException

    # Get task
    task = await get_task(task_id, team_id)
    if not task:
        raise APIException(
            code="TASK_NOT_FOUND",
            message=f"Task {task_id} not found",
            status_code=404,
        )

    # Verify task is AI-assigned
    assignee_type = task.get("assignee_type")
    if assignee_type not in ["agent", "ai"]:
        raise APIException(
            code="TASK_NOT_AI_ASSIGNED",
            message="Task is not assigned to an AI agent",
            status_code=400,
            details={"assignee_type": assignee_type},
        )

    # Create audit event for agent execution trigger
    await create_event(
        team_id=team_id,
        event_type="agent_execution_triggered",
        payload={
            "task_id": str(task_id),
            "assignee_id": str(task.get("assignee_id")) if task.get("assignee_id") else None,
        },
        user_id=user.user_id,
        task_id=task_id,
    )

    return {
        "task_id": str(task_id),
        "status": "execution_initiated",
        "message": "AI agent execution has been triggered",
    }


@router.post("/{task_id}/execution/decision", response_model=TaskApprovalResponse)
async def execution_decision(
    task_id: UUID = Path(..., description="Task ID"),
    request: TaskApprovalRequest = ...,
    team_id: UUID = Query(..., description="Team ID"),
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> TaskApprovalResponse:
    """
    Handle approval/rejection decision for AI task execution outputs.

    This endpoint allows human reviewers to approve or reject the results
    of AI agent execution. This is similar to the approve endpoint but
    specifically for execution outputs.

    Requires:
    - Authentication (JWT token)
    - Team membership
    """
    # Use the same approval service but with a different event type
    service = TaskApprovalService()
    result = await service.approve_task(
        task_id=task_id,
        team_id=team_id,
        approved=request.approved,
        user=user,
        comment=request.comment,
    )
    
    # Create additional event for execution decision
    from backend.app.db.queries import create_event
    await create_event(
        team_id=team_id,
        event_type="execution_decision",
        payload={
            "task_id": str(task_id),
            "approved": request.approved,
            "comment": request.comment,
        },
        user_id=user.user_id,
        task_id=task_id,
    )
    
    from datetime import datetime
    from uuid import UUID as UUIDType
    return TaskApprovalResponse(
        task_id=UUIDType(result["task_id"]),
        approved=result["approved"],
        approved_at=datetime.fromisoformat(result["approved_at"]) if result.get("approved_at") else None,
        approved_by=result.get("approved_by"),
        comment=result.get("comment"),
    )
