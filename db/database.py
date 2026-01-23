"""Database connection management and session factory using SQLModel."""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel

from config import settings


# Create database engine with connection pooling
engine: Engine = create_engine(
    str(settings.effective_database_url),
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=settings.db_pool_pre_ping,
    echo=settings.is_development,  # Log SQL queries in development
    future=True,  # Use SQLAlchemy 2.0 style
)

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Session: Database session
        
    Example:
        ```python
        def some_function():
            db = next(get_db())
            try:
                # Use db session
                pass
            finally:
                db.close()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions with automatic rollback on error.
    
    Yields:
        Session: Database session
        
    Example:
        ```python
        with get_db_context() as db:
            # Use db session
            # Automatically commits on success, rolls back on error
            pass
        ```
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.
    
    This should be called after all models are imported.
    """
    SQLModel.metadata.create_all(engine)


def close_db() -> None:
    """Close all database connections."""
    engine.dispose()

