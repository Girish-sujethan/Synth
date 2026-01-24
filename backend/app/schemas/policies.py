"""Policy-related schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.schemas.common import BaseRequest, BaseResponse


# ============================================================================
# POLICY REQUEST SCHEMAS
# ============================================================================


class PolicyCreateRequest(BaseRequest):
    """Request schema for creating a policy."""

    name: str = Field(..., min_length=1, description="Policy name (non-empty)")
    policy_md: Optional[str] = Field(None, min_length=1, description="Policy markdown content (non-empty)")
    description_md: Optional[str] = Field(None, description="Description markdown")
    orchestration_policy_md: Optional[str] = Field(None, min_length=1, description="Orchestration policy markdown")
    ai_safety_policy_md: Optional[str] = Field(None, min_length=1, description="AI safety policy markdown")
    tagging_rules_md: Optional[str] = Field(None, min_length=1, description="Tagging rules markdown")


class PolicyUpdateRequest(BaseRequest):
    """Request schema for updating a policy."""

    name: Optional[str] = Field(None, min_length=1, description="Policy name")
    policy_md: Optional[str] = Field(None, min_length=1, description="Policy markdown content")
    description_md: Optional[str] = Field(None, description="Description markdown")
    orchestration_policy_md: Optional[str] = Field(None, min_length=1, description="Orchestration policy markdown")
    ai_safety_policy_md: Optional[str] = Field(None, min_length=1, description="AI safety policy markdown")
    tagging_rules_md: Optional[str] = Field(None, min_length=1, description="Tagging rules markdown")


# ============================================================================
# POLICY RESPONSE SCHEMAS
# ============================================================================


class PolicyResponse(BaseResponse):
    """Response schema for a policy."""

    id: UUID = Field(..., description="Policy ID")
    team_id: UUID = Field(..., description="Team ID")
    name: str = Field(..., description="Policy name")
    policy_md: Optional[str] = Field(None, description="Policy markdown content")
    description_md: Optional[str] = Field(None, description="Description markdown")
    orchestration_policy_md: Optional[str] = Field(None, description="Orchestration policy markdown")
    ai_safety_policy_md: Optional[str] = Field(None, description="AI safety policy markdown")
    tagging_rules_md: Optional[str] = Field(None, description="Tagging rules markdown")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class PolicyListResponse(BaseResponse):
    """Response schema for a list of policies."""

    policies: list[PolicyResponse] = Field(..., description="List of policies")
    total: int = Field(..., description="Total number of policies")
