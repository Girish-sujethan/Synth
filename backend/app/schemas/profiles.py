"""Profile-related schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.schemas.common import BaseRequest, BaseResponse, UserLevel


# ============================================================================
# PROFILE REQUEST SCHEMAS
# ============================================================================


class ProfileCreateRequest(BaseRequest):
    """Request schema for creating a profile."""

    name: Optional[str] = Field(None, description="User name")
    email: Optional[str] = Field(None, description="User email")
    skills: Optional[dict] = Field(None, description="User skills as JSONB")
    level: Optional[UserLevel] = Field(None, description="User level")
    velocity: float = Field(default=0.0, ge=0.0, description="Work velocity")
    load: float = Field(default=0.0, ge=0.0, description="Current work load")


class ProfileUpdateRequest(BaseRequest):
    """Request schema for updating a profile."""

    name: Optional[str] = Field(None, description="User name")
    email: Optional[str] = Field(None, description="User email")
    skills: Optional[dict] = Field(None, description="User skills as JSONB")
    level: Optional[UserLevel] = Field(None, description="User level")
    velocity: Optional[float] = Field(None, ge=0.0, description="Work velocity")
    load: Optional[float] = Field(None, ge=0.0, description="Current work load")


# ============================================================================
# PROFILE RESPONSE SCHEMAS
# ============================================================================


class ProfileResponse(BaseResponse):
    """Response schema for a profile."""

    id: UUID = Field(..., description="Profile ID")
    user_id: str = Field(..., description="User ID")
    team_id: UUID = Field(..., description="Team ID")
    name: Optional[str] = Field(None, description="User name")
    email: Optional[str] = Field(None, description="User email")
    skills: dict = Field(default_factory=dict, description="User skills")
    level: Optional[UserLevel] = Field(None, description="User level")
    velocity: float = Field(default=0.0, description="Work velocity")
    load: float = Field(default=0.0, description="Current work load")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ProfileListResponse(BaseResponse):
    """Response schema for a list of profiles."""

    profiles: list[ProfileResponse] = Field(..., description="List of profiles")
    total: int = Field(..., description="Total number of profiles")
