"""FastAPI dependency functions for authentication, database sessions, and common validations."""

from typing import Optional, Generator
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from db.database import get_db
from api.auth import extract_user_from_token
from core.exceptions import AuthenticationError, AuthorizationError
from core.security import api_key_manager
from core.logging import get_logger
from services.storage import StorageService

logger = get_logger(__name__)

# Global storage service instance
_storage_service: StorageService | None = None


def get_storage_service() -> StorageService:
    """
    Get or create storage service instance.
    
    Returns:
        StorageService instance
    """
    global _storage_service
    
    if _storage_service is None:
        _storage_service = StorageService()
    
    return _storage_service


def get_database_session() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Yields:
        Database session
    """
    yield from get_db()


def get_current_user(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        authorization: Authorization header (Bearer token)
        x_api_key: Optional API key header
        
    Returns:
        User information dictionary
        
    Raises:
        AuthenticationError: If authentication fails
    """
    # Check for API key first (if provided)
    if x_api_key:
        if api_key_manager.validate_api_key(x_api_key):
            # API key authentication successful
            # Return a system user or allow API key access
            return {
                "id": "api_key",
                "email": None,
                "metadata": {"auth_type": "api_key"},
            }
        else:
            raise AuthenticationError("Invalid API key")
    
    # Check for JWT token
    if not authorization:
        raise AuthenticationError("Authorization header is required")
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise AuthenticationError("Invalid authorization scheme. Use 'Bearer'")
    except ValueError:
        raise AuthenticationError("Invalid authorization header format")
    
    # Extract user from token
    user = extract_user_from_token(token)
    if not user:
        raise AuthenticationError("Invalid or expired token")
    
    return user


def get_optional_user(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> Optional[dict]:
    """
    Dependency to get current user if authenticated, otherwise None.
    
    Args:
        authorization: Authorization header (Bearer token)
        x_api_key: Optional API key header
        
    Returns:
        User information dictionary if authenticated, None otherwise
    """
    try:
        return get_current_user(authorization, x_api_key)
    except AuthenticationError:
        return None


def require_permission(permission: str):
    """
    Dependency factory to require specific permission.
    
    Args:
        permission: Required permission string
        
    Returns:
        Dependency function that checks for permission
    """
    def permission_checker(
        current_user: dict = Depends(get_current_user)
    ) -> dict:
        user_permissions = current_user.get("metadata", {}).get("permissions", [])
        
        if permission not in user_permissions:
            raise AuthorizationError(
                f"Permission '{permission}' is required"
            )
        
        return current_user
    
    return permission_checker

