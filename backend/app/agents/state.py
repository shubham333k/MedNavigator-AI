"""
LangGraph agent state definitions for the diagnostic assistant.

Uses TypedDict (required by LangGraph StateGraph) alongside a Pydantic model
for API serialization. Both representations carry the same fields.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict

from pydantic import BaseModel, Field


# ── LangGraph-compatible state (TypedDict) ────────────────────────────────────
# LangGraph StateGraph nodes receive and return this TypedDict.

class DiagnosticStateDict(TypedDict, total=False):
    """
    Full mutable state passed between LangGraph nodes.
    Each field may be absent on initialisation; nodes fill it progressively.
    """

    # Patient information
    symptoms: List[str]
    patient_age: Optional[int]
    patient_sex: Optional[str]
    medical_history: List[str]
    current_medications: List[str]

    # Diagnostic progress
    stage: str                          # gathering | reasoning | refining | complete
    iteration: int
    max_iterations: int

    # Retrieved evidence
    retrieved_context: str
    retrieved_documents: List[Dict[str, Any]]

    # Conversation thread
    messages: List[Dict[str, str]]
    follow_up_questions: List[str]
    clinician_responses: List[str]

    # Output
    differential_diagnoses: List[Dict[str, Any]]
    current_analysis: str
    final_message: str
    is_complete: bool


def make_initial_state(
    symptoms: List[str],
    patient_age: Optional[int] = None,
    patient_sex: Optional[str] = None,
    medical_history: Optional[List[str]] = None,
    current_medications: Optional[List[str]] = None,
) -> DiagnosticStateDict:
    """Return a fully initialised DiagnosticStateDict ready for the graph."""
    return DiagnosticStateDict(
        symptoms=symptoms,
        patient_age=patient_age,
        patient_sex=patient_sex,
        medical_history=medical_history or [],
        current_medications=current_medications or [],
        stage="gathering",
        iteration=0,
        max_iterations=3,
        retrieved_context="",
        retrieved_documents=[],
        messages=[],
        follow_up_questions=[],
        clinician_responses=[],
        differential_diagnoses=[],
        current_analysis="",
        final_message="",
        is_complete=False,
    )


# ── Pydantic model (kept for backwards-compat & API serialisation) ────────────

class DiagnosticState(BaseModel):
    """
    Pydantic mirror of DiagnosticStateDict.
    Used only for type-safe API handling; the graph itself operates on
    DiagnosticStateDict.
    """

    # Patient information
    symptoms: List[str] = Field(default_factory=list)
    patient_age: Optional[int] = None
    patient_sex: Optional[str] = None
    medical_history: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)

    # Diagnostic state
    stage: str = Field(default="gathering")
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

    @classmethod
    def from_dict(cls, d: DiagnosticStateDict) -> "DiagnosticState":
        """Convert a LangGraph state dict back to a Pydantic model."""
        return cls(**d)
