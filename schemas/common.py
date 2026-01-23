"""Common API response schemas for consistent formatting across all endpoints."""

from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Base response model for all API responses."""
    
    success: bool = Field(description="Whether the request was successful")
    message: Optional[str] = Field(default=None, description="Response message")
    data: Optional[T] = Field(default=None, description="Response data")


class SuccessResponse(BaseResponse[T]):
    """Success response model."""
    
    success: bool = Field(default=True, description="Request was successful")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {}
            }
        }


class ErrorResponse(BaseResponse[None]):
    """Error response model."""
    
    success: bool = Field(default=False, description="Request failed")
    error: Optional[str] = Field(default=None, description="Error message")
    details: Optional[dict] = Field(default=None, description="Error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "An error occurred",
                "error": "ValidationError",
                "details": {"field": "email", "message": "Invalid email format"}
            }
        }


class PaginatedResponse(BaseResponse[List[T]]):
    """Paginated response model."""
    
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")
    total: int = Field(description="Total number of items")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_previous: bool = Field(description="Whether there is a previous page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Items retrieved successfully",
                "data": [],
                "page": 1,
                "page_size": 10,
                "total": 100,
                "total_pages": 10,
                "has_next": True,
                "has_previous": False
            }
        }


class MessageResponse(BaseResponse[None]):
    """Simple message response model."""
    
    success: bool = Field(default=True, description="Request was successful")
    data: None = Field(default=None, description="No data in response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": None
            }
        }

