"""Event/audit-related schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.schemas.common import BaseRequest, BaseResponse


# ============================================================================
# EVENT REQUEST SCHEMAS
# ============================================================================


class EventCreateRequest(BaseRequest):
    """Request schema for creating an audit event."""

    event_type: str = Field(..., min_length=1, description="Event type (non-empty)")
    payload: dict = Field(default_factory=dict, description="Event payload as JSONB")
    task_id: Optional[UUID] = Field(None, description="Related task ID")


# ============================================================================
# EVENT RESPONSE SCHEMAS
# ============================================================================


class EventResponse(BaseResponse):
    """Response schema for an audit event."""

    id: UUID = Field(..., description="Event ID")
    team_id: UUID = Field(..., description="Team ID")
    event_type: str = Field(..., description="Event type")
    payload: dict = Field(default_factory=dict, description="Event payload")
    user_id: Optional[str] = Field(None, description="User ID who triggered the event")
    created_at: datetime = Field(..., description="Event timestamp")


class EventListResponse(BaseResponse):
    """Response schema for a list of events."""

    events: list[EventResponse] = Field(..., description="List of events")
    total: int = Field(..., description="Total number of events")
