"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    This endpoint does not require authentication and is used to verify
    that the API is running and responsive.
    """
    return {"status": "healthy"}
