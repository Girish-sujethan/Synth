"""Team member-related schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.schemas.auth import UserRole
from backend.app.schemas.common import BaseRequest, BaseResponse, UserLevel


# ============================================================================
# TEAM MEMBER REQUEST SCHEMAS
# ============================================================================


class TeamMemberCreateRequest(BaseRequest):
    """Request schema for adding a team member."""

    user_id: str = Field(..., description="User ID")
    role: UserRole = Field(..., description="Team role")
    display_name: Optional[str] = Field(None, description="Display name")
    skills: Optional[dict] = Field(None, description="User skills")
    level: Optional[UserLevel] = Field(None, description="User level")
    velocity: Optional[float] = Field(None, ge=0.0, description="Work velocity (>= 0)")
    current_load: Optional[float] = Field(None, ge=0.0, description="Current work load (>= 0)")


class TeamMemberUpdateRequest(BaseRequest):
    """Request schema for updating a team member."""

    role: Optional[UserRole] = Field(None, description="Team role")
    display_name: Optional[str] = Field(None, description="Display name")
    skills: Optional[dict] = Field(None, description="User skills")
    level: Optional[UserLevel] = Field(None, description="User level")
    velocity: Optional[float] = Field(None, ge=0.0, description="Work velocity")
    current_load: Optional[float] = Field(None, ge=0.0, description="Current work load")


# ============================================================================
# TEAM MEMBER RESPONSE SCHEMAS
# ============================================================================


class TeamMemberResponse(BaseResponse):
    """Response schema for a team member."""

    id: UUID = Field(..., description="Member ID")
    team_id: UUID = Field(..., description="Team ID")
    user_id: str = Field(..., description="User ID")
    role: UserRole = Field(..., description="Team role")
    display_name: Optional[str] = Field(None, description="Display name")
    skills: Optional[dict] = Field(None, description="User skills")
    level: Optional[UserLevel] = Field(None, description="User level")
    velocity: float = Field(default=0.0, description="Work velocity")
    current_load: float = Field(default=0.0, description="Current work load")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class TeamMemberListResponse(BaseResponse):
    """Response schema for a list of team members."""

    members: list[TeamMemberResponse] = Field(..., description="List of team members")
    total: int = Field(..., description="Total number of members")
