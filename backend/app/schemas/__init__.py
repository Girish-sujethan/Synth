"""Pydantic schemas for request/response validation."""

# Common schemas
from backend.app.schemas.common import (
    AssigneeType,
    AssignmentRisk,
    BaseRequest,
    BaseResponse,
    FibonacciSize,
    LowercaseTags,
    TaskSize,
    UserLevel,
    normalize_tags,
    validate_fibonacci_size,
)

# Auth schemas
from backend.app.schemas.auth import TokenData, UserRole

# Error schemas
from backend.app.schemas.errors import ErrorDetail, ErrorResponse

# Column schemas
from backend.app.schemas.columns import (
    ColumnCreateRequest,
    ColumnDeleteRequest,
    ColumnListResponse,
    ColumnReorderRequest,
    ColumnResponse,
    ColumnUpdateRequest,
    TaskMoveRequest,
    TaskMoveResponse,
)

# Entity schemas
from backend.app.schemas.agents import (
    AIAgentCreateRequest,
    AIAgentListResponse,
    AIAgentResponse,
    AIAgentUpdateRequest,
)
from backend.app.schemas.board import (
    BoardColumnCreateRequest,
    BoardColumnListResponse,
    BoardColumnResponse,
    BoardColumnUpdateRequest,
    BoardResponse,
)
from backend.app.schemas.events import (
    EventCreateRequest,
    EventListResponse,
    EventResponse,
)
from backend.app.schemas.members import (
    TeamMemberCreateRequest,
    TeamMemberListResponse,
    TeamMemberResponse,
    TeamMemberUpdateRequest,
)
from backend.app.schemas.policies import (
    PolicyCreateRequest,
    PolicyListResponse,
    PolicyResponse,
    PolicyUpdateRequest,
)
from backend.app.schemas.profiles import (
    ProfileCreateRequest,
    ProfileListResponse,
    ProfileResponse,
    ProfileUpdateRequest,
)
from backend.app.schemas.tasks import (
    SubtaskDetailItem,
    TaskApprovalRequest,
    TaskApprovalResponse,
    TaskCreateRequest,
    TaskDetailResponse,
    TaskHistoryEvent,
    TaskListResponse,
    TaskOrchestrateRequest,
    TaskResponse,
    TaskSplitRequest,
    TaskUpdateRequest,
)
from backend.app.schemas.teams import (
    TeamCreateRequest,
    TeamListResponse,
    TeamResponse,
    TeamUpdateRequest,
)

__all__ = [
    # Common
    "BaseRequest",
    "BaseResponse",
    "AssigneeType",
    "AssignmentRisk",
    "UserLevel",
    "TaskSize",
    "FibonacciSize",
    "LowercaseTags",
    "normalize_tags",
    "validate_fibonacci_size",
    # Auth
    "UserRole",
    "TokenData",
    # Errors
    "ErrorResponse",
    "ErrorDetail",
    # Tasks
    "TaskCreateRequest",
    "TaskUpdateRequest",
    "TaskSplitRequest",
    "TaskOrchestrateRequest",
    "TaskResponse",
    "TaskDetailResponse",
    "SubtaskDetailItem",
    "TaskHistoryEvent",
    "TaskApprovalRequest",
    "TaskApprovalResponse",
    "TaskListResponse",
    # Teams
    "TeamCreateRequest",
    "TeamUpdateRequest",
    "TeamResponse",
    "TeamListResponse",
    # Team Members
    "TeamMemberCreateRequest",
    "TeamMemberUpdateRequest",
    "TeamMemberResponse",
    "TeamMemberListResponse",
    # Profiles
    "ProfileCreateRequest",
    "ProfileUpdateRequest",
    "ProfileResponse",
    "ProfileListResponse",
    # AI Agents
    "AIAgentCreateRequest",
    "AIAgentUpdateRequest",
    "AIAgentResponse",
    "AIAgentListResponse",
    # Board Columns
    "BoardColumnCreateRequest",
    "BoardColumnUpdateRequest",
    "BoardColumnResponse",
    "BoardColumnListResponse",
    "BoardResponse",
    # Policies
    "PolicyCreateRequest",
    "PolicyUpdateRequest",
    "PolicyResponse",
    "PolicyListResponse",
    # Events
    "EventCreateRequest",
    "EventResponse",
    "EventListResponse",
    # Columns
    "ColumnResponse",
    "ColumnListResponse",
    "ColumnCreateRequest",
    "ColumnUpdateRequest",
    "ColumnReorderRequest",
    "ColumnDeleteRequest",
    "TaskMoveRequest",
    "TaskMoveResponse",
]
