"""Column management schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from backend.app.schemas.common import BaseRequest, BaseResponse


# ============================================================================
# COLUMN REQUEST SCHEMAS
# ============================================================================


class ColumnUpdateRequest(BaseRequest):
    """Request schema for updating a column."""

    display_name: Optional[str] = Field(None, min_length=1, description="Display name")
    position: Optional[int] = Field(None, ge=0, description="Column position")
    wip_limit: Optional[int] = Field(None, ge=0, description="Work in progress limit")


class ColumnReorderRequest(BaseRequest):
    """Request schema for reordering columns."""

    ordered_keys: list[str] = Field(..., min_items=1, description="Ordered list of column keys")

    @field_validator("ordered_keys")
    @classmethod
    def validate_keys(cls, v: list[str]) -> list[str]:
        """Validate keys are not empty."""
        if not v:
            raise ValueError("ordered_keys cannot be empty")
        return v


class ColumnCreateRequest(BaseRequest):
    """Request schema for creating a column."""

    key: str = Field(..., min_length=1, description="Column key (lowercase slug)")
    display_name: str = Field(..., min_length=1, description="Display name")
    position: Optional[int] = Field(None, ge=0, description="Column position")
    wip_limit: Optional[int] = Field(None, ge=0, description="Work in progress limit")

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        """Validate key is lowercase slug format."""
        import re
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError("Key must be lowercase alphanumeric with hyphens only")
        return v.lower()


class ColumnDeleteRequest(BaseRequest):
    """Request schema for deleting a column."""

    migrate_tasks_to: Optional[str] = Field(None, description="Target column key for task migration")


class TaskMoveRequest(BaseRequest):
    """Request schema for moving a task."""

    column_key: str = Field(..., min_length=1, description="Target column key")
    note: Optional[str] = Field(None, description="Optional note for the move")
    client_action: Optional[str] = Field(None, description="Client action identifier")


# ============================================================================
# COLUMN RESPONSE SCHEMAS
# ============================================================================


class ColumnResponse(BaseResponse):
    """Response schema for a column."""

    id: str = Field(..., description="Column ID")
    key: str = Field(..., description="Column key")
    display_name: str = Field(..., description="Display name")
    name: str = Field(..., description="Column name")
    position: int = Field(..., description="Column position")
    wip_limit: Optional[int] = Field(None, description="Work in progress limit")
    is_locked: bool = Field(default=False, description="Whether column is locked")


class ColumnListResponse(BaseResponse):
    """Response schema for a list of columns."""

    columns: list[ColumnResponse] = Field(..., description="List of columns")


class TaskMoveResponse(BaseResponse):
    """Response schema for task movement."""

    id: str = Field(..., description="Task ID")
    column_key: str = Field(..., description="New column key")
    column_id: str = Field(..., description="New column ID")
