"""Schemas package with base response models and common data structures."""

from schemas.common import (
    BaseResponse,
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
    MessageResponse,
)

__all__ = [
    "BaseResponse",
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "MessageResponse",
]

