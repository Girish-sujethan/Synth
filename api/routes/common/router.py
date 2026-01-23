"""Common router with health check, version info, and system status endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_session
from db.health import check_database_health
from db.migrations import get_migration_status
from schemas.common import SuccessResponse, MessageResponse
from config import settings
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/common",
    tags=["common"]
)


@router.get("/health", response_model=SuccessResponse[dict])
async def health_check(db: Session = Depends(get_session)):
    """
    Health check endpoint for the common module.
    
    Returns:
        Health status with database and migration information
    """
    db_health = check_database_health()
    migration_status = get_migration_status()
    
    return SuccessResponse(
        message="System health check",
        data={
            "status": "healthy" if db_health["status"] == "healthy" else "degraded",
            "database": {
                "connected": db_health["connected"],
                "response_time_ms": db_health["response_time_ms"],
            },
            "migrations": {
                "current_revision": migration_status["current_revision"],
                "head_revision": migration_status["head_revision"],
                "is_up_to_date": migration_status["is_up_to_date"],
            },
            "environment": settings.environment,
        }
    )


@router.get("/version", response_model=SuccessResponse[dict])
async def get_version():
    """
    Get API version information.
    
    Returns:
        API version details
    """
    return SuccessResponse(
        message="API version information",
        data={
            "version": "1.0.0",
            "api_version": "v1",
            "name": "Synth API",
            "description": "FastAPI backend with Supabase authentication",
        }
    )


@router.get("/status", response_model=SuccessResponse[dict])
async def get_system_status(db: Session = Depends(get_session)):
    """
    Get comprehensive system status.
    
    Returns:
        System status including database, migrations, and configuration
    """
    db_health = check_database_health()
    migration_status = get_migration_status()
    
    return SuccessResponse(
        message="System status",
        data={
            "system": {
                "status": "operational" if db_health["status"] == "healthy" else "degraded",
                "environment": settings.environment,
            },
            "database": {
                "status": db_health["status"],
                "connected": db_health["connected"],
                "response_time_ms": db_health["response_time_ms"],
            },
            "migrations": {
                "current_revision": migration_status["current_revision"],
                "head_revision": migration_status["head_revision"],
                "is_up_to_date": migration_status["is_up_to_date"],
            },
        }
    )


@router.get("/info", response_model=SuccessResponse[dict])
async def get_api_info():
    """
    Get API information and capabilities.
    
    Returns:
        API information including available modules and features
    """
    return SuccessResponse(
        message="API information",
        data={
            "name": "Synth API",
            "version": "1.0.0",
            "api_version": "v1",
            "modules": [
                "common",
                "graph",
                "validator",
            ],
            "features": [
                "authentication",
                "database",
                "migrations",
                "storage",
            ],
        }
    )

