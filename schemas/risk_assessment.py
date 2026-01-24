"""Pydantic schemas for risk assessment models."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from models.risk_assessment import RiskLevel


# Task Schemas
class TaskBase(BaseModel):
    """Base task schema with common fields."""
    
    description: str = Field(description="Task description")
    status: Optional[str] = Field(default="pending", description="Task status")


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass


class TaskRead(TaskBase):
    """Schema for reading task data."""
    
    id: int = Field(description="Task ID")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    class Config:
        from_attributes = True


# ReasoningTrace Schemas
class ReasoningTraceBase(BaseModel):
    """Base reasoning trace schema."""
    
    trace_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="JSON data containing the reasoning trace information"
    )


class ReasoningTraceCreate(ReasoningTraceBase):
    """Schema for creating a new reasoning trace."""
    pass


class ReasoningTraceRead(ReasoningTraceBase):
    """Schema for reading reasoning trace data."""
    
    id: int = Field(description="Reasoning trace ID")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    class Config:
        from_attributes = True


# Risk Factor Schema
class RiskFactorSchema(BaseModel):
    """Schema for risk factor objects."""
    
    factor: str = Field(description="Risk factor name/identifier")
    description: str = Field(description="Description of the risk factor")
    severity: str = Field(description="Severity level of the risk factor")


# TaskRiskAssessment Schemas
class TaskRiskAssessmentBase(BaseModel):
    """Base task risk assessment schema."""
    
    task_id: int = Field(description="Reference to the parent task")
    subtask_id: Optional[str] = Field(
        default=None,
        description="Identifier for the subtask being assessed"
    )
    risk_level: RiskLevel = Field(description="Overall risk level (low, medium, high)")
    risk_factors: Optional[List[RiskFactorSchema]] = Field(
        default=None,
        description="Array of risk factor objects with factor, description, and severity fields"
    )
    mitigation_suggestions: Optional[str] = Field(
        default=None,
        description="Suggestions for mitigating identified risks"
    )
    reasoning_trace_id: Optional[int] = Field(
        default=None,
        description="Reference to the reasoning trace that generated this assessment"
    )


class TaskRiskAssessmentCreate(TaskRiskAssessmentBase):
    """Schema for creating a new task risk assessment."""
    pass


class TaskRiskAssessmentRead(TaskRiskAssessmentBase):
    """Schema for reading task risk assessment data."""
    
    id: int = Field(description="Risk assessment ID")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    class Config:
        from_attributes = True


# API Response Schemas
class AssessRisksResponse(BaseModel):
    """Response schema for POST /tasks/{task_id}/assess-risks endpoint."""
    
    task_id: int = Field(description="Task ID for which risk assessment was triggered")
    status: str = Field(default="assessing_risks", description="Status of the assessment process")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "status": "assessing_risks"
            }
        }


class AssessmentItem(BaseModel):
    """Individual assessment item in the risk assessment response."""
    
    id: int = Field(description="Risk assessment ID")
    subtask_id: Optional[str] = Field(description="Subtask identifier")
    risk_level: RiskLevel = Field(description="Overall risk level")
    risk_factors: Optional[List[RiskFactorSchema]] = Field(
        default=None,
        description="Array of risk factor objects"
    )
    mitigation_suggestions: Optional[str] = Field(
        default=None,
        description="Suggestions for mitigating identified risks"
    )
    
    class Config:
        from_attributes = True


class RiskAssessmentResponse(BaseModel):
    """Response schema for GET /tasks/{task_id}/risk-assessment endpoint."""
    
    task_id: int = Field(description="Task ID")
    assessments: List[AssessmentItem] = Field(
        description="Array of risk assessments for the task"
    )
    created_at: datetime = Field(description="Timestamp when assessments were created")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "assessments": [
                    {
                        "id": 1,
                        "subtask_id": "subtask_1",
                        "risk_level": "medium",
                        "risk_factors": [
                            {
                                "factor": "complexity",
                                "description": "High complexity in implementation",
                                "severity": "medium"
                            }
                        ],
                        "mitigation_suggestions": "Break down into smaller subtasks"
                    }
                ],
                "created_at": "2026-01-23T19:00:00Z"
            }
        }

