"""Board API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends

from backend.app.core.middleware import get_current_user, require_team_membership
from backend.app.schemas.auth import TokenData
from backend.app.schemas.board import BoardResponse
from backend.app.services.task_service import TaskService

router = APIRouter(prefix="/board", tags=["board"])


@router.get("", response_model=BoardResponse)
async def get_board(
    team_id: UUID = Query(..., description="Team ID"),
    user: TokenData = Depends(get_current_user),
    _: TokenData = Depends(require_team_membership),
) -> BoardResponse:
    """
    Get board data for a team.

    Returns columns and tasks organized by column, with computed subtask_count.

    Requires:
    - Authentication (JWT token)
    - Team membership
    """
    board_data = await TaskService.get_board(team_id, user)
    return BoardResponse(**board_data)
