"""Common validators and base schemas."""

from enum import Enum
from typing import Annotated, Any

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# ENUMS
# ============================================================================


class AssigneeType(str, Enum):
    """Assignee type enumeration."""

    HUMAN = "human"
    AI = "ai"
    UNASSIGNED = "unassigned"


class AssignmentRisk(str, Enum):
    """Assignment risk level enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UserLevel(str, Enum):
    """User level enumeration."""

    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"


class TaskSize(int, Enum):
    """Task size enumeration (Fibonacci values)."""

    ONE = 1
    TWO = 2
    THREE = 3
    FIVE = 5
    EIGHT = 8


# ============================================================================
# VALIDATORS
# ============================================================================


def validate_fibonacci_size(value: int) -> int:
    """Validate that size is a Fibonacci number (1, 2, 3, 5, 8)."""
    valid_sizes = {1, 2, 3, 5, 8}
    if value not in valid_sizes:
        raise ValueError(f"Size must be one of: {', '.join(map(str, valid_sizes))}")
    return value


def normalize_tags(tags: list[str] | None) -> list[str]:
    """Normalize tags to lowercase."""
    if tags is None:
        return []
    return [tag.lower().strip() for tag in tags if tag.strip()]


# ============================================================================
# BASE SCHEMAS
# ============================================================================


class BaseRequest(BaseModel):
    """Base request schema."""

    model_config = {"extra": "forbid"}


class BaseResponse(BaseModel):
    """Base response schema."""

    model_config = {"extra": "forbid", "from_attributes": True}


# ============================================================================
# FIELD TYPES WITH VALIDATION
# ============================================================================

# Fibonacci size field type
FibonacciSize = Annotated[
    int,
    Field(description="Task size (Fibonacci: 1, 2, 3, 5, 8)"),
]

# Lowercase tags field type - use as type hint, validation happens in models
LowercaseTags = list[str]

# UUID field type
UUIDField = Annotated[
    str,
    Field(description="UUID identifier", pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
]
