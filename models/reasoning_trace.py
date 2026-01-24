"""ReasoningTrace model for storing LLM reasoning traces."""

from typing import Optional, Dict, Any
from sqlmodel import Field, Column, JSON
from models.base import BaseModel


class ReasoningTrace(BaseModel, table=True):
    """
    ReasoningTrace model for storing LLM reasoning traces.
    
    This model stores the reasoning process and trace data from LLM operations,
    which can be referenced by risk assessments.
    """
    
    __tablename__ = "reasoning_traces"
    
    # Reasoning trace data stored as JSON
    trace_data: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="JSON data containing the reasoning trace information"
    )

