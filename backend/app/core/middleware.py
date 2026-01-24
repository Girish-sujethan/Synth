"""Authentication and authorization middleware."""

from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from backend.app.core.config import settings
from backend.app.core.exceptions import AuthenticationError, TeamAccessError
from backend.app.schemas.auth import TokenData, UserRole
from backend.app.schemas.errors import ErrorResponse

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """
    Validate JWT token and extract user information.

    Extracts user ID from the 'sub' claim in the JWT token.
    
    Note: SUPABASE_JWT_SECRET must be set in .env file.
    Get it from Supabase Dashboard > Project Settings > API > JWT Secret.
    """
    token = credentials.credentials

    if not settings.supabase_jwt_secret:
        raise AuthenticationError(
            "JWT secret not configured. Set SUPABASE_JWT_SECRET in .env file."
        )

    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token: missing 'sub' claim")

        email: Optional[str] = payload.get("email")
        role_str: Optional[str] = payload.get("role")
        role: Optional[UserRole] = None
        if role_str:
            try:
                role = UserRole(role_str)
            except ValueError:
                pass

        return TokenData(user_id=user_id, email=email, role=role)

    except JWTError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")


async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> Optional[TokenData]:
    """
    Optionally validate JWT token and extract user information.

    Returns None if no token is provided. Used for endpoints that work
    with or without authentication.
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except AuthenticationError:
        return None


def require_role(allowed_roles: list[UserRole]):
    """
    Dependency factory for role-based access control.

    Usage:
        @app.get("/admin")
        async def admin_endpoint(user: TokenData = Depends(require_role([UserRole.ADMIN]))):
            ...
    """

    async def role_checker(user: TokenData = Depends(get_current_user)) -> TokenData:
        """Check if user has required role."""
        if user.role not in allowed_roles:
            from backend.app.core.exceptions import AuthorizationError

            raise AuthorizationError(
                f"Required role: {', '.join(r.value for r in allowed_roles)}",
                details={"user_role": user.role.value if user.role else None},
            )
        return user

    return role_checker


async def require_team_membership(
    team_id: str,
    user: TokenData = Depends(get_current_user),
) -> TokenData:
    """
    Dependency to verify user is a member of the specified team.

    Usage:
        @app.get("/team/{team_id}/data")
        async def team_data(team_id: str, user: TokenData = Depends(require_team_membership)):
            ...

    Note: The team_id parameter should come from the path parameter in the route.
    FastAPI will inject it automatically.

    Args:
        team_id: The team ID to check membership for (from path parameter)
        user: The authenticated user

    Returns:
        TokenData if user is a team member

    Raises:
        TeamAccessError: If user is not a member of the team
    """
    from uuid import UUID
    from backend.app.db.queries import get_team_member

    try:
        team_uuid = UUID(team_id)
    except ValueError:
        raise TeamAccessError(team_id, details={"error": "Invalid team ID format"})

    team_member = await get_team_member(team_id=team_uuid, user_id=user.user_id)
    if not team_member:
        raise TeamAccessError(team_id)
    return user


def create_error_response(exception: Exception) -> tuple[ErrorResponse, int]:
    """
    Convert exception to standard error response format.

    Args:
        exception: The exception to convert

    Returns:
        Tuple of (ErrorResponse, status_code)
    """
    from backend.app.core.exceptions import APIException

    if isinstance(exception, APIException):
        return (
            ErrorResponse.create(
                code=exception.code,
                message=exception.message,
                details=exception.details,
            ),
            exception.status_code,
        )

    # Default error response
    return (
        ErrorResponse.create(
            code="INTERNAL_ERROR",
            message="An internal error occurred",
            details={"type": type(exception).__name__},
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
