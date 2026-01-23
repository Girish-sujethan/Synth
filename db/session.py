"""Database session management with dependency injection for FastAPI routes."""

from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends

from db.database import get_db


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency to get database session.
    
    This is the primary dependency for FastAPI route handlers.
    The session is automatically closed after the request completes.
    
    Yields:
        Database session
        
    Example:
        ```python
        from fastapi import APIRouter, Depends
        from db.session import get_session
        from sqlalchemy.orm import Session
        
        router = APIRouter()
        
        @router.get("/items")
        def get_items(db: Session = Depends(get_session)):
            # Use db session
            return {"items": []}
        ```
    """
    yield from get_db()


# Alias for convenience
get_db_session = get_session

