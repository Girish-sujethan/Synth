"""Example route demonstrating authentication and authorization."""

from fastapi import APIRouter, Depends

from backend.app.core.middleware import get_current_user, require_role, require_team_membership
from backend.app.schemas.auth import TokenData, UserRole

router = APIRouter(prefix="/example", tags=["example"])


@router.get("/protected")
async def protected_endpoint(user: TokenData = Depends(get_current_user)) -> dict:
    """
    Example protected endpoint requiring authentication.

    This endpoint requires a valid JWT token in the Authorization header.
    """
    return {
        "message": "This is a protected endpoint",
        "user_id": user.user_id,
        "email": user.email,
    }


@router.get("/admin-only")
async def admin_endpoint(user: TokenData = Depends(require_role([UserRole.ADMIN]))) -> dict:
    """
    Example endpoint requiring admin role.

    Only users with the 'admin' role can access this endpoint.
    """
    return {
        "message": "This endpoint requires admin role",
        "user_id": user.user_id,
        "role": user.role.value if user.role else None,
    }


@router.get("/team/{team_id}")
async def team_endpoint(
    team_id: str,
    user: TokenData = Depends(require_team_membership),
) -> dict:
    """
    Example endpoint requiring team membership.

    Users must be members of the specified team to access this endpoint.
    The team_id is extracted from the path parameter and used to verify membership.
    """
    return {
        "message": f"User {user.user_id} is a member of team {team_id}",
        "team_id": team_id,
        "user_id": user.user_id,
    }
