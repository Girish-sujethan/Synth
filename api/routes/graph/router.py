"""Graph router with placeholder structure for future graph operations."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_session
from schemas.common import SuccessResponse, MessageResponse
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/graph",
    tags=["graph"]
)


@router.get("/", response_model=SuccessResponse[dict])
async def graph_info():
    """
    Get graph module information.
    
    Returns:
        Graph module status and capabilities
    """
    return SuccessResponse(
        message="Graph module is available",
        data={
            "module": "graph",
            "status": "ready",
            "description": "Graph operations and analysis",
            "endpoints": [
                "GET /api/v1/graph/",
            ],
        }
    )


@router.get("/status", response_model=SuccessResponse[dict])
async def graph_status(db: Session = Depends(get_session)):
    """
    Get graph module status.
    
    Returns:
        Graph module status information
    """
    return SuccessResponse(
        message="Graph module status",
        data={
            "module": "graph",
            "status": "operational",
            "features": [
                "graph_operations",
                "graph_analysis",
            ],
        }
    )

