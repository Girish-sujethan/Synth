"""AI agent-related schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from backend.app.schemas.common import BaseRequest, BaseResponse, LowercaseTags, normalize_tags


# ============================================================================
# AI AGENT REQUEST SCHEMAS
# ============================================================================


class AIAgentCreateRequest(BaseRequest):
    """Request schema for creating an AI agent."""

    name: str = Field(..., min_length=1, description="Agent name (non-empty)")
    capabilities_md: Optional[str] = Field(None, description="Capabilities markdown")
    limits_md: Optional[str] = Field(None, description="Limits markdown")
    tags: Optional[LowercaseTags] = Field(None, description="Agent tags (lowercase)")
    tags_good_at: Optional[LowercaseTags] = Field(None, description="Tags agent is good at")
    tags_avoid: Optional[LowercaseTags] = Field(None, description="Tags agent should avoid")
    requires_review: Optional[bool] = Field(None, description="Whether agent requires review")

    @field_validator("tags", "tags_good_at", "tags_avoid", mode="before")
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Normalize tags to lowercase."""
        return normalize_tags(v) if v is not None else None


class AIAgentUpdateRequest(BaseRequest):
    """Request schema for updating an AI agent."""

    name: Optional[str] = Field(None, min_length=1, description="Agent name")
    capabilities_md: Optional[str] = Field(None, description="Capabilities markdown")
    limits_md: Optional[str] = Field(None, description="Limits markdown")
    tags: Optional[LowercaseTags] = Field(None, description="Agent tags (lowercase)")
    tags_good_at: Optional[LowercaseTags] = Field(None, description="Tags agent is good at")
    tags_avoid: Optional[LowercaseTags] = Field(None, description="Tags agent should avoid")
    requires_review: Optional[bool] = Field(None, description="Whether agent requires review")

    @field_validator("tags", "tags_good_at", "tags_avoid", mode="before")
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Normalize tags to lowercase."""
        return normalize_tags(v) if v is not None else None


# ============================================================================
# AI AGENT RESPONSE SCHEMAS
# ============================================================================


class AIAgentResponse(BaseResponse):
    """Response schema for an AI agent."""

    id: UUID = Field(..., description="Agent ID")
    team_id: UUID = Field(..., description="Team ID")
    name: str = Field(..., description="Agent name")
    capabilities_md: Optional[str] = Field(None, description="Capabilities markdown")
    limits_md: Optional[str] = Field(None, description="Limits markdown")
    tags: list[str] = Field(default_factory=list, description="Agent tags")
    tags_good_at: list[str] = Field(default_factory=list, description="Tags agent is good at")
    tags_avoid: list[str] = Field(default_factory=list, description="Tags agent should avoid")
    requires_review: bool = Field(default=False, description="Whether agent requires review")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class AIAgentListResponse(BaseResponse):
    """Response schema for a list of AI agents."""

    agents: list[AIAgentResponse] = Field(..., description="List of AI agents")
    total: int = Field(..., description="Total number of agents")
