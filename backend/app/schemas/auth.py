"""Authentication and authorization schemas."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """User role enumeration."""

    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"


class TokenData(BaseModel):
    """JWT token data extracted from claims."""

    user_id: str = Field(..., description="User ID from 'sub' claim")
    email: Optional[str] = Field(None, description="User email")
    role: Optional[UserRole] = Field(None, description="User role")


class TeamMember(BaseModel):
    """Team member information."""

    user_id: str = Field(..., description="User ID")
    team_id: str = Field(..., description="Team ID")
    role: UserRole = Field(..., description="User role in the team")
