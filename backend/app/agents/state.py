"""
LangGraph agent state definitions for the diagnostic assistant.
"""

from typing import List, Optional, Dict, Any, Annotated
from pydantic import BaseModel, Field
import operator


class DiagnosticState(BaseModel):
    """
    State object for the LangGraph diagnostic workflow.
    Tracks the full conversation and diagnostic progress.
    """

    # Patient information
    symptoms: List[str] = Field(default_factory=list)
    patient_age: Optional[int] = None
    patient_sex: Optional[str] = None
    medical_history: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)

    # Diagnostic state
    stage: str = Field(default="gathering")  # gathering, reasoning, refining, complete
    iteration: int = Field(default=0)
    max_iterations: int = Field(default=3)

    # Retrieved context
    retrieved_context: str = Field(default="")
    retrieved_documents: List[Dict[str, Any]] = Field(default_factory=list)

    # Conversation history
    messages: List[Dict[str, str]] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)
    clinician_responses: List[str] = Field(default_factory=list)

    # Results
    differential_diagnoses: List[Dict[str, Any]] = Field(default_factory=list)
    current_analysis: str = Field(default="")
    final_message: str = Field(default="")
    is_complete: bool = Field(default=False)

    model_config = {"arbitrary_types_allowed": True}
