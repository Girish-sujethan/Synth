"""Task-related schemas."""

from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from backend.app.schemas.common import (
    AssigneeType,
    AssignmentRisk,
    BaseRequest,
    BaseResponse,
    FibonacciSize,
    LowercaseTags,
    TaskSize,
    normalize_tags,
    validate_fibonacci_size,
)


# ============================================================================
# TASK REQUEST SCHEMAS
# ============================================================================


class TaskCreateRequest(BaseRequest):
    """Request schema for creating a task."""

    title: str = Field(..., min_length=1, description="Task title (non-empty)")
    description: Optional[str] = Field(None, description="Task description")
    parent_id: Optional[UUID] = Field(None, description="Parent task ID for hierarchical structure")
    size: Optional[FibonacciSize] = Field(None, description="Task size (Fibonacci: 1, 2, 3, 5, 8)")
    tags: Optional[LowercaseTags] = Field(None, description="Task tags (lowercase)")
    column_key: Optional[str] = Field(None, description="Board column key")
    assignee_type: Optional[AssigneeType] = Field(None, description="Assignee type")
    assignee_id: Optional[UUID] = Field(None, description="Assignee ID (user or agent)")
    assignment_risk: Optional[AssignmentRisk] = Field(None, description="Assignment risk level")

    @field_validator("size")
    @classmethod
    def validate_size(cls, v: Optional[int]) -> Optional[int]:
        """Validate Fibonacci size."""
        if v is not None:
            return validate_fibonacci_size(v)
        return v

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Normalize tags to lowercase."""
        return normalize_tags(v) if v is not None else None


class TaskUpdateRequest(BaseRequest):
    """Request schema for updating a task."""

    title: Optional[str] = Field(None, min_length=1, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: Optional[str] = Field(None, description="Task status")
    size: Optional[FibonacciSize] = Field(None, description="Task size (Fibonacci: 1, 2, 3, 5, 8)")
    tags: Optional[LowercaseTags] = Field(None, description="Task tags (lowercase)")
    column_key: Optional[str] = Field(None, description="Board column key")
    assignee_type: Optional[AssigneeType] = Field(None, description="Assignee type")
    assignee_id: Optional[UUID] = Field(None, description="Assignee ID")
    assignment_risk: Optional[AssignmentRisk] = Field(None, description="Assignment risk level")
    override_flag: Optional[bool] = Field(None, description="Override flag")

    @field_validator("size")
    @classmethod
    def validate_size(cls, v: Optional[int]) -> Optional[int]:
        """Validate Fibonacci size."""
        if v is not None:
            return validate_fibonacci_size(v)
        return v

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Normalize tags to lowercase."""
        return normalize_tags(v) if v is not None else None


class TaskMoveRequest(BaseRequest):
    """Request schema for moving a task."""

    column_key: str = Field(..., min_length=1, description="Target column key")
    note: Optional[str] = Field(None, description="Optional note for the move")
    client_action: Optional[str] = Field(None, description="Client action identifier")


class TaskSplitRequest(BaseRequest):
    """Request schema for splitting a task."""

    instructions: Optional[str] = Field(None, description="Optional instructions for splitting")
    policy_version: Optional[str] = Field(None, description="Policy version to use")


class TaskOrchestrateRequest(BaseRequest):
    """Request schema for orchestrating tasks."""

    instructions: Optional[str] = Field(None, description="Optional orchestration instructions")
    strategy: Optional[str] = Field(None, description="Orchestration strategy")


# ============================================================================
# TASK RESPONSE SCHEMAS
# ============================================================================


class TaskHistoryEvent(BaseModel):
    """Schema for a task history event from audit trail."""

    id: UUID = Field(..., description="Event ID")
    event_type: str = Field(..., description="Event type")
    created_at: datetime = Field(..., description="Event timestamp")
    user_id: Optional[str] = Field(None, description="User who triggered the event")
    payload: dict = Field(default_factory=dict, description="Event payload data")


class TaskResponse(BaseResponse):
    """Response schema for a task."""

    id: UUID = Field(..., description="Task ID")
    team_id: UUID = Field(..., description="Team ID")
    parent_id: Optional[UUID] = Field(None, description="Parent task ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: Optional[str] = Field(None, description="Task status")
    size: Optional[int] = Field(None, description="Task size")
    tags: list[str] = Field(default_factory=list, description="Task tags")
    column_id: Optional[UUID] = Field(None, description="Board column ID")
    column_key: Optional[str] = Field(None, description="Board column key")
    assignee_type: Optional[AssigneeType] = Field(None, description="Assignee type")
    assignee_id: Optional[UUID] = Field(None, description="Assignee ID")
    assignment_risk: Optional[AssignmentRisk] = Field(None, description="Assignment risk level")
    override_flag: bool = Field(default=False, description="Override flag")
    subtask_count: int = Field(default=0, description="Number of subtasks")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    audit_history: Optional[list[TaskHistoryEvent]] = Field(None, description="Complete task history from audit trail")


class SubtaskDetailItem(BaseModel):
    """Minimal subtask information for preview in parent task detail."""

    id: UUID = Field(..., description="Subtask ID")
    title: str = Field(..., description="Subtask title")
    column_key: Optional[str] = Field(None, description="Subtask column key")
    assignee_display_name: Optional[str] = Field(None, description="Assignee display name")


class TaskDetailResponse(BaseResponse):
    """Comprehensive task detail response with joined display fields."""

    # Canonical task fields
    id: UUID = Field(..., description="Task ID")
    team_id: UUID = Field(..., description="Team ID")
    parent_id: Optional[UUID] = Field(None, description="Parent task ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    column_key: Optional[str] = Field(None, description="Board column key")
    tags: list[str] = Field(default_factory=list, description="Task tags")
    size: Optional[int] = Field(None, description="Task size")
    assignee_type: Optional[AssigneeType] = Field(None, description="Assignee type")
    assignee_id: Optional[UUID] = Field(None, description="Assignee ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Derived display fields
    assignee_display_name: Optional[str] = Field(None, description="Assignee display name (from profiles or ai_agents)")
    parent_title: Optional[str] = Field(None, description="Parent task title (if subtask)")

    # Orchestration context
    assignment_reason: Optional[str] = Field(None, description="Assignment reason")
    assignment_risk: Optional[AssignmentRisk] = Field(None, description="Assignment risk level")

    # Subtasks preview (for parent tasks)
    subtasks_preview: Optional[list[SubtaskDetailItem]] = Field(None, description="Minimal subtask information (for parent tasks)")


class TaskListResponse(BaseResponse):
    """Response schema for a list of tasks."""

    tasks: list[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")


class TaskMoveResponse(BaseResponse):
    """Response schema for task movement."""

    task_id: UUID = Field(..., description="Task ID")
    from_column_key: Optional[str] = Field(None, description="Source column key")
    to_column_key: str = Field(..., description="Target column key")
    updated_at: datetime = Field(..., description="Update timestamp")


class SubtaskPreview(BaseModel):
    """Schema for a subtask in a split preview."""

    title: str = Field(..., description="Subtask title")
    description: str = Field(..., description="Subtask description")
    size: int = Field(..., description="Subtask size (Fibonacci: 1, 2, 3, 5, 8)")
    tags: list[str] = Field(..., description="Subtask tags")


class TaskSplitPreviewResponse(BaseResponse):
    """Response schema for task split preview."""

    subtasks: list[SubtaskPreview] = Field(..., description="List of proposed subtasks")
    policy_version: str = Field(..., description="Policy version hash")
    model: str = Field(..., description="LLM model used")
    parent_task_id: UUID = Field(..., description="Parent task ID")


class TaskSplitConfirmRequest(BaseRequest):
    """Request schema for confirming a task split."""

    subtasks: list[SubtaskPreview] = Field(..., description="Subtasks to create (may be user-edited)")


class TaskSplitConfirmResponse(BaseResponse):
    """Response schema for confirmed task split."""

    parent_task_id: UUID = Field(..., description="Parent task ID")
    subtask_ids: list[UUID] = Field(..., description="Created subtask IDs")
    subtask_count: int = Field(..., description="Number of subtasks created")
    policy_version: str = Field(..., description="Policy version hash")
    model: str = Field(..., description="LLM model used")


class AssignmentPreview(BaseModel):
    """Schema for an assignment in orchestration preview."""

    subtask_index: int = Field(..., description="Subtask index (1-based)")
    assignee_type: str = Field(..., description="Assignee type: human or ai")
    assignee_id: str = Field(..., description="Assignee ID (user or agent UUID)")
    assignment_risk: str = Field(..., description="Assignment risk: low, medium, or high")
    reasoning: str = Field(..., description="Explanation for the assignment")


class TaskOrchestrationPreviewResponse(BaseResponse):
    """Response schema for task orchestration preview."""

    assignments: list[AssignmentPreview] = Field(..., description="List of proposed assignments")
    policy_version: str = Field(..., description="Policy version hash")
    model: str = Field(..., description="LLM model used")
    parent_task_id: UUID = Field(..., description="Parent task ID")


class TaskOrchestrationConfirmRequest(BaseRequest):
    """Request schema for confirming task orchestration."""

    assignments: list[AssignmentPreview] = Field(..., description="Assignments to confirm (may be user-edited)")


class AssignmentResult(BaseModel):
    """Schema for a confirmed assignment result."""

    subtask_id: UUID = Field(..., description="Subtask ID")
    assignee_type: str = Field(..., description="Assignee type")
    assignee_id: UUID = Field(..., description="Assignee ID")
    assignment_risk: str = Field(..., description="Assignment risk level")


class TaskOrchestrationConfirmResponse(BaseResponse):
    """Response schema for confirmed task orchestration."""

    parent_task_id: UUID = Field(..., description="Parent task ID")
    assignments: list[AssignmentResult] = Field(..., description="Confirmed assignments")
    assignment_count: int = Field(..., description="Number of assignments")
    policy_version: str = Field(..., description="Policy version hash")
    model: str = Field(..., description="LLM model used")


class TaskApprovalRequest(BaseRequest):
    """Request schema for task approval."""

    approved: bool = Field(..., description="Whether the task is approved")
    comment: Optional[str] = Field(None, description="Optional comment on approval decision")


class TaskApprovalResponse(BaseResponse):
    """Response schema for task approval."""

    task_id: UUID = Field(..., description="Task ID")
    approved: bool = Field(..., description="Approval status")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    approved_by: Optional[str] = Field(None, description="User ID who approved")
    comment: Optional[str] = Field(None, description="Approval comment")
