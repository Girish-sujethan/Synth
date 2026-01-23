"""Common dependencies shared across multiple domain modules."""

from typing import Generator
from sqlalchemy.orm import Session

from db.session import get_session
from api.dependencies import get_current_user, get_optional_user
from core.logging import get_logger

logger = get_logger(__name__)


def get_db_session() -> Generator[Session, None, None]:
    """
    Get database session dependency.
    
    This is a convenience alias for consistency across modules.
    
    Yields:
        Database session
    """
    yield from get_session()


def require_authentication():
    """
    Dependency factory for requiring authentication.
    
    Returns:
        Dependency function that requires authenticated user
    """
    return get_current_user


def optional_authentication():
    """
    Dependency factory for optional authentication.
    
    Returns:
        Dependency function that optionally returns authenticated user
    """
    return get_optional_user

