"""Column management API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from backend.app.core.middleware import get_current_user, require_team_membership
from backend.app.schemas.auth import TokenData
from backend.app.schemas.columns import (
    ColumnCreateRequest,
    ColumnDeleteRequest,
    ColumnListResponse,
    ColumnReorderRequest,
    ColumnResponse,
    ColumnUpdateRequest,
    TaskMoveRequest,
    TaskMoveResponse,
)
from backend.app.services.column_service import ColumnService

router = APIRouter(prefix="/teams", tags=["columns"])


@router.get("/{team_id}/columns", response_model=ColumnListResponse)
async def list_columns(
    team_id: UUID,
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> ColumnListResponse:
    """
    List all columns for a team.

    Returns ordered column configuration with all fields.

    Requires:
    - Authentication (JWT token)
    - Team membership
    """
    columns = await ColumnService.list_columns(team_id, user)
    return ColumnListResponse(columns=[ColumnResponse(**col) for col in columns])


@router.get("/{team_id}/columns/{column_key}", response_model=ColumnResponse)
async def get_column(
    team_id: UUID,
    column_key: str,
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> ColumnResponse:
    """
    Get a column by key.

    Requires:
    - Authentication (JWT token)
    - Team membership
    """
    column = await ColumnService.get_column(team_id, column_key, user)
    return ColumnResponse(**column)


@router.patch("/{team_id}/columns/{column_key}", response_model=ColumnResponse)
async def update_column(
    team_id: UUID,
    column_key: str,
    request: ColumnUpdateRequest,
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> ColumnResponse:
    """
    Update a column.

    Can update display_name, position, and wip_limit.
    Cannot modify key or locked columns.

    Requires:
    - Authentication (JWT token)
    - Team membership
    - Admin role
    """
    column = await ColumnService.update_column(
        team_id=team_id,
        column_key=column_key,
        display_name=request.display_name,
        position=request.position,
        wip_limit=request.wip_limit,
        user=user,
    )
    return ColumnResponse(**column)


@router.put("/{team_id}/columns/reorder", response_model=ColumnListResponse)
async def reorder_columns(
    team_id: UUID,
    request: ColumnReorderRequest,
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> ColumnListResponse:
    """
    Bulk reorder columns.

    Requires:
    - Authentication (JWT token)
    - Team membership
    - Admin role
    """
    columns = await ColumnService.reorder_columns(team_id, request.ordered_keys, user)
    return ColumnListResponse(columns=[ColumnResponse(**col) for col in columns])


@router.post("/{team_id}/columns", status_code=status.HTTP_201_CREATED, response_model=ColumnResponse)
async def create_column(
    team_id: UUID,
    request: ColumnCreateRequest,
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> ColumnResponse:
    """
    Create a new column.

    Requires:
    - Authentication (JWT token)
    - Team membership
    - Admin role
    """
    column = await ColumnService.create_column(
        team_id=team_id,
        key=request.key,
        display_name=request.display_name,
        position=request.position,
        wip_limit=request.wip_limit,
        user=user,
    )
    return ColumnResponse(**column)


@router.delete("/{team_id}/columns/{column_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(
    team_id: UUID,
    column_key: str,
    request: ColumnDeleteRequest = None,
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> None:
    """
    Delete a column.

    If column has tasks, migrate_tasks_to parameter is required.

    Requires:
    - Authentication (JWT token)
    - Team membership
    - Admin role
    """
    migrate_tasks_to = request.migrate_tasks_to if request else None
    await ColumnService.delete_column(team_id, column_key, migrate_tasks_to, user)


@router.post("/{team_id}/tasks/{task_id}/move", response_model=TaskMoveResponse)
async def move_task_via_columns(
    team_id: UUID,
    task_id: UUID,
    request: TaskMoveRequest,
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> TaskMoveResponse:
    """
    Move a task to a different column (alternative endpoint).

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
