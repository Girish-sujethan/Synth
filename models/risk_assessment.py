"""TaskRiskAssessment model for storing risk assessment data."""

from typing import Optional, List, Dict, Any
from enum import Enum
from sqlmodel import Field, Column, JSON
from models.base import BaseModel


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskFactor(BaseModel):
    """
    Risk factor structure for JSONB storage.
    
    This is a Pydantic model for validation, not a database table.
    """
    
    factor: str = Field(description="Risk factor name/identifier")
    description: str = Field(description="Description of the risk factor")
    severity: str = Field(description="Severity level of the risk factor")


class TaskRiskAssessment(BaseModel, table=True):
    """
    TaskRiskAssessment model for storing risk assessment data.
    
    This model stores risk analysis data for subtasks, supporting informed
    task assignment decisions.
    """
    
    __tablename__ = "task_risk_assessments"
    
    # Foreign key to tasks table
    task_id: int = Field(
        foreign_key="tasks.id",
        index=True,
        description="Reference to the parent task"
    )
    
    # Subtask identifier (optional, can be null for top-level task assessments)
    subtask_id: Optional[str] = Field(
        default=None,
        index=True,
        description="Identifier for the subtask being assessed"
    )
    
    # Risk level enum
    risk_level: RiskLevel = Field(
        index=True,
        description="Overall risk level (low, medium, high)"
    )
    
    # Risk factors stored as JSONB array
    # Each element is a RiskFactor object with factor, description, and severity
    risk_factors: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Array of risk factor objects with factor, description, and severity fields"
    )
    
    # Mitigation suggestions
    mitigation_suggestions: Optional[str] = Field(
        default=None,
        description="Suggestions for mitigating identified risks"
    )
    
    # Foreign key to reasoning_traces table (optional)
    reasoning_trace_id: Optional[int] = Field(
        default=None,
        foreign_key="reasoning_traces.id",
        index=True,
        description="Reference to the reasoning trace that generated this assessment"
    )

