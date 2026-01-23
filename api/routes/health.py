"""Health check endpoint with database connectivity and migrations status."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_session
from db.health import check_database_health
from db.migrations import get_migration_status
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "api"
    }


@router.get("/database")
async def database_health_check(db: Session = Depends(get_session)):
    """
    Database health check with connectivity test.
    
    Args:
        db: Database session
        
    Returns:
        Database health status
    """
    health = check_database_health()
    
    return {
        "status": health["status"],
        "database": {
            "connected": health["connected"],
            "response_time_ms": health["response_time_ms"],
            "version": health.get("database_version"),
        },
        "error": health.get("error"),
    }


@router.get("/migrations")
async def migrations_health_check():
    """
    Check database migration status.
    
    Returns:
        Migration status information
    """
    status = get_migration_status()
    
    return {
        "status": "up_to_date" if status["is_up_to_date"] else "needs_migration",
        "current_revision": status["current_revision"],
        "head_revision": status["head_revision"],
        "needs_migration": status["needs_migration"],
    }


@router.get("/full")
async def full_health_check(db: Session = Depends(get_session)):
    """
    Comprehensive health check including database and migrations.
    
    Args:
        db: Database session
        
    Returns:
        Complete health status
    """
    db_health = check_database_health()
    migration_status = get_migration_status()
    
    overall_status = "healthy"
    if db_health["status"] != "healthy":
        overall_status = "unhealthy"
    elif not migration_status["is_up_to_date"]:
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "database": {
            "status": db_health["status"],
            "connected": db_health["connected"],
            "response_time_ms": db_health["response_time_ms"],
            "version": db_health.get("database_version"),
        },
        "migrations": {
            "current_revision": migration_status["current_revision"],
            "head_revision": migration_status["head_revision"],
            "is_up_to_date": migration_status["is_up_to_date"],
        },
        "service": "api",
    }

