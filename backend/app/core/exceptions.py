"""Custom exception classes."""

from typing import Any, Dict, Optional


class APIException(Exception):
    """Base API exception with error code and details."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize API exception."""
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(APIException):
    """Authentication error (401)."""

    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        """Initialize authentication error."""
        super().__init__(
            code="AUTH_REQUIRED",
            message=message,
            status_code=401,
            details=details,
        )


class AuthorizationError(APIException):
    """Authorization error (403)."""

    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        """Initialize authorization error."""
        super().__init__(
            code="ACCESS_DENIED",
            message=message,
            status_code=403,
            details=details,
        )


class TeamAccessError(AuthorizationError):
    """Team access error (403)."""

    def __init__(self, team_id: str, details: Optional[Dict[str, Any]] = None):
        """Initialize team access error."""
        super().__init__(
            message=f"User is not a member of team {team_id}",
            details={"team_id": team_id, **(details or {})},
        )


class DatabaseError(APIException):
    """Database operation error (500)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize database error."""
        super().__init__(
            code="DATABASE_ERROR",
            message=message,
            status_code=500,
            details=details or {},
        )
