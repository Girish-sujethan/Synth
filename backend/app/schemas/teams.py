"""Team-related schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.schemas.auth import UserRole
from backend.app.schemas.common import BaseRequest, BaseResponse


# ============================================================================
# TEAM REQUEST SCHEMAS
# ============================================================================


class TeamCreateRequest(BaseRequest):
    """Request schema for creating a team."""

    name: str = Field(..., min_length=1, description="Team name (non-empty)")


class TeamUpdateRequest(BaseRequest):
    """Request schema for updating a team."""

    name: Optional[str] = Field(None, min_length=1, description="Team name")


# ============================================================================
# TEAM RESPONSE SCHEMAS
# ============================================================================


class TeamResponse(BaseResponse):
    """Response schema for a team."""

    id: UUID = Field(..., description="Team ID")
    name: str = Field(..., description="Team name")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class TeamListResponse(BaseResponse):
    """Response schema for a list of teams."""

    teams: list[TeamResponse] = Field(..., description="List of teams")
    total: int = Field(..., description="Total number of teams")
