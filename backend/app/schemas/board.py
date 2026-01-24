"""Board column-related schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.schemas.common import BaseRequest, BaseResponse


# ============================================================================
# BOARD COLUMN REQUEST SCHEMAS
# ============================================================================


class BoardColumnCreateRequest(BaseRequest):
    """Request schema for creating a board column."""

    name: str = Field(..., min_length=1, description="Column name")
    position: int = Field(..., ge=0, description="Column position")
    key: Optional[str] = Field(None, description="Column key")
    display_name: Optional[str] = Field(None, description="Display name")
    wip_limit: Optional[int] = Field(None, ge=0, description="Work in progress limit")
    is_locked: Optional[bool] = Field(None, description="Whether column is locked")
    workflow_config: Optional[dict] = Field(None, description="Workflow configuration")


class BoardColumnUpdateRequest(BaseRequest):
    """Request schema for updating a board column."""

    name: Optional[str] = Field(None, min_length=1, description="Column name")
    position: Optional[int] = Field(None, ge=0, description="Column position")
    key: Optional[str] = Field(None, description="Column key")
    display_name: Optional[str] = Field(None, description="Display name")
    wip_limit: Optional[int] = Field(None, ge=0, description="Work in progress limit")
    is_locked: Optional[bool] = Field(None, description="Whether column is locked")
    workflow_config: Optional[dict] = Field(None, description="Workflow configuration")


# ============================================================================
# BOARD COLUMN RESPONSE SCHEMAS
# ============================================================================


class BoardColumnResponse(BaseResponse):
    """Response schema for a board column."""

    id: UUID = Field(..., description="Column ID")
    team_id: UUID = Field(..., description="Team ID")
    name: str = Field(..., description="Column name")
    position: int = Field(..., description="Column position")
    key: Optional[str] = Field(None, description="Column key")
    display_name: Optional[str] = Field(None, description="Display name")
    wip_limit: Optional[int] = Field(None, description="Work in progress limit")
    is_locked: bool = Field(default=False, description="Whether column is locked")
    workflow_config: dict = Field(default_factory=dict, description="Workflow configuration")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class BoardColumnListResponse(BaseResponse):
    """Response schema for a list of board columns."""

    columns: list[BoardColumnResponse] = Field(..., description="List of board columns")
    total: int = Field(..., description="Total number of columns")


class BoardResponse(BaseResponse):
    """Response schema for a board with columns and tasks."""

    team_id: UUID = Field(..., description="Team ID")
    columns: list[BoardColumnResponse] = Field(..., description="Board columns")
    tasks: list[dict] = Field(default_factory=list, description="Tasks organized by column")
