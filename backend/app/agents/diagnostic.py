"""
LangGraph-powered diagnostic assistant agent.

Implements a real LangGraph StateGraph with typed nodes as specified in the
blueprint (§3.1 / §5.3):

  gather_information → reason → refine → complete
        ↑_________________↑ (conditional loop while not complete)

The graph preserves the same external API contract (DiagnosticResponse),
so the FastAPI routes require no changes.
"""

from __future__ import annotations

import re
import uuid
import logging
from typing import Dict, Any, Optional, List

from langchain_core.messages import SystemMessage, HumanMessage

# LangGraph imports
from langgraph.graph import StateGraph, END

from app.agents.state import DiagnosticStateDict, DiagnosticState, make_initial_state
from app.core.llm import get_llm_manager
from app.core.prompts import (
    DIAGNOSTIC_SYSTEM_PROMPT,
    DIAGNOSTIC_GATHERING_TEMPLATE,
    DIAGNOSTIC_REFINEMENT_TEMPLATE,
)
from app.rag.retriever import get_retriever
from app.models.schemas import DiagnosticResponse, Diagnosis, Citation

logger = logging.getLogger(__name__)

# ── In-memory session store (use Redis in production) ─────────────────────────
_active_sessions: Dict[str, DiagnosticStateDict] = {}


# ─────────────────────────────────────────────────────────────────────────────
# Node functions
# Each node receives the full state dict, mutates it, and returns the delta.
# ─────────────────────────────────────────────────────────────────────────────

def _node_gather_information(state: DiagnosticStateDict) -> DiagnosticStateDict:
    """
    Information Gathering Node (blueprint §5.3 step 2).
    Queries the vector DB for medical literature matching the patient symptoms.
    """
    retriever = get_retriever(n_results=8)

    symptom_query = " ".join(state.get("symptoms", []))
    history = state.get("medical_history", [])
    if history:
        symptom_query += " " + " ".join(history)

    documents = retriever.retrieve(symptom_query, n_results=8)
    context = retriever.format_context(documents)

    logger.info(f"[gather_information] Retrieved {len(documents)} documents for symptoms")

    return {
        **state,
        "retrieved_documents": documents,
        "retrieved_context": context,
        "stage": "reasoning",
    }


def _node_reason(state: DiagnosticStateDict) -> DiagnosticStateDict:
    """
    Reasoning Node (blueprint §5.3 step 3).
    Analyses retrieved conditions and formulates initial differential diagnoses.
    """
    llm = get_llm_manager()

    prompt = DIAGNOSTIC_GATHERING_TEMPLATE.format(
        symptoms=", ".join(state.get("symptoms", [])),
        age=state.get("patient_age") or "Not provided",
        sex=state.get("patient_sex") or "Not provided",
        medical_history=", ".join(state.get("medical_history", [])) or "None provided",
        medications=", ".join(state.get("current_medications", [])) or "None provided",
        context=state.get("retrieved_context", ""),
    )

    messages = [
        SystemMessage(content=DIAGNOSTIC_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    analysis = llm.invoke(messages)
    follow_ups = _extract_follow_up(analysis)

    logger.info(
        f"[reason] Reasoning complete. Generated {len(follow_ups)} follow-up question(s)"
    )

    updated_messages = list(state.get("messages", [])) + [
        {"role": "agent", "content": analysis}
    ]

    return {
        **state,
        "current_analysis": analysis,
        "follow_up_questions": follow_ups,
        "messages": updated_messages,
        "stage": "refining",
    }


def _node_refine(state: DiagnosticStateDict) -> DiagnosticStateDict:
    """
    Refinement Node (blueprint §5.3 step 4).
    Processes clinician follow-up responses and updates the differential.
    """
    llm = get_llm_manager()
    retriever = get_retriever(n_results=5)

    clinician_responses = state.get("clinician_responses", [])
    latest_response = clinician_responses[-1] if clinician_responses else ""

    # Retrieve additional context based on new information
    combined_query = " ".join(state.get("symptoms", [])) + " " + latest_response
    extra_docs = retriever.retrieve(combined_query, n_results=5)
    extra_context = retriever.format_context(extra_docs)

    prompt = DIAGNOSTIC_REFINEMENT_TEMPLATE.format(
        symptoms=", ".join(state.get("symptoms", [])),
        age=state.get("patient_age") or "Not provided",
        sex=state.get("patient_sex") or "Not provided",
        medical_history=", ".join(state.get("medical_history", [])) or "None provided",
        previous_analysis=state.get("current_analysis", ""),
        clinician_response=latest_response,
        context=extra_context,
    )

    messages_payload = [
        SystemMessage(content=DIAGNOSTIC_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    analysis = llm.invoke(messages_payload)
    follow_ups = _extract_follow_up(analysis)

    iteration = state.get("iteration", 0) + 1
    max_iter = state.get("max_iterations", 3)

    # Determine if the workflow should terminate
    is_complete = (iteration >= max_iter) or (not follow_ups)
    stage = "complete" if is_complete else "refining"

    updated_messages = list(state.get("messages", [])) + [
        {"role": "agent", "content": analysis}
    ]

    logger.info(
        f"[refine] Iteration {iteration}/{max_iter}. "
        f"Complete={is_complete}. Follow-ups={len(follow_ups)}"
    )

    return {
        **state,
        "current_analysis": analysis,
        "follow_up_questions": follow_ups,
        "messages": updated_messages,
        "iteration": iteration,
        "stage": stage,
        "is_complete": is_complete,
    }


def _should_continue(state: DiagnosticStateDict) -> str:
    """
    Conditional edge — decides whether to loop back or end the graph.
    Returns the name of the next node or END.
    """
    if state.get("is_complete"):
        return END
    if state.get("iteration", 0) >= state.get("max_iterations", 3):
        return END
    # If there's a pending clinician response we haven't processed yet,
    # stay in the refine cycle; otherwise wait (graph pauses at 'refining').
    return END   # graph ends; subsequent calls re-enter at _node_refine


# ─────────────────────────────────────────────────────────────────────────────
# Build the StateGraph
# ─────────────────────────────────────────────────────────────────────────────

def _build_graph() -> Any:
    """
    Construct and compile the LangGraph StateGraph for differential diagnosis.

    Workflow (blueprint §5.3):
      gather_information → reason → [refine ↔ clinician] → complete
    """
    graph = StateGraph(DiagnosticStateDict)

    # Register nodes
    graph.add_node("gather_information", _node_gather_information)
    graph.add_node("reason", _node_reason)
    graph.add_node("refine", _node_refine)

    # Entry point
    graph.set_entry_point("gather_information")

    # Static edges
    graph.add_edge("gather_information", "reason")
    graph.add_edge("reason", END)          # pause: wait for clinician input
    graph.add_edge("refine", END)          # pause: wait for next clinician input

    return graph.compile()


# Singleton compiled graph
_compiled_graph = None


def _get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = _build_graph()
    return _compiled_graph


# ─────────────────────────────────────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────────────────────────────────────

def _extract_follow_up(response: str) -> List[str]:
    """Extract follow-up questions from the agent's response."""
    questions: List[str] = []
    for line in response.split("\n"):
        line = line.strip()
        if line.endswith("?") and len(line) > 15:
            clean = re.sub(r"^[-•*>1-9][\.\)]\s*", "", line).strip()
            if clean:
                questions.append(clean)
    return questions[:3]


def _parse_diagnoses(analysis: str) -> List[Diagnosis]:
    """
    Parse the LLM's analysis into structured Diagnosis objects.
    Blueprint §5.3 step 5: ranked diagnoses with supporting evidence.
    """
    diagnoses: List[Diagnosis] = []

    pattern = r"\*\*(.+?)\*\*.*?(?:Likelihood|Probability):\s*(High|Medium|Low)"
    matches = re.findall(pattern, analysis, re.IGNORECASE)
    likelihood_scores = {"high": 0.85, "medium": 0.55, "low": 0.25}

    for condition, likelihood in matches:
        diagnoses.append(
            Diagnosis(
                condition=condition.strip(),
                likelihood=likelihood.capitalize(),
                confidence_score=likelihood_scores.get(likelihood.lower(), 0.5),
                supporting_evidence=[analysis[:500]],
                recommended_tests=None,
                citations=[],
            )
        )

    if not diagnoses:
        diagnoses.append(
            Diagnosis(
                condition="See detailed analysis above",
                likelihood="Medium",
                confidence_score=0.5,
                supporting_evidence=[analysis[:500]],
                recommended_tests=None,
                citations=[],
            )
        )

    return diagnoses


def _build_response(session_id: str, state: DiagnosticStateDict) -> DiagnosticResponse:
    """Map the internal graph state to the external API response schema."""
    follow_up = None
    fqs = state.get("follow_up_questions", [])
    if fqs and not state.get("is_complete"):
        follow_up = fqs[0]

    diagnoses = None
    if state.get("is_complete") or state.get("stage") == "complete":
        diagnoses = _parse_diagnoses(state.get("current_analysis", ""))

    return DiagnosticResponse(
        session_id=session_id,
        stage=state.get("stage", "gathering"),
        message=state.get("current_analysis", ""),
        follow_up_question=follow_up,
        differential_diagnoses=diagnoses,
        is_complete=state.get("is_complete", False),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Public API — same interface as before; routes require no changes
# ─────────────────────────────────────────────────────────────────────────────

class DiagnosticAgent:
    """
    Wraps the compiled LangGraph StateGraph and manages sessions.

    Nodes execute in order: gather_information → reason → (refine)* → END
    Each call to `start_session` or `respond` runs the graph from the
    appropriate entry node and stores the resulting state for the next turn.
    """

    def start_session(
        self,
        symptoms: List[str],
        patient_age: Optional[int] = None,
        patient_sex: Optional[str] = None,
        medical_history: Optional[List[str]] = None,
        current_medications: Optional[List[str]] = None,
    ) -> DiagnosticResponse:
        """
        Start a new diagnostic session.
        Runs: gather_information → reason → END (paused for clinician input).
        """
        session_id = str(uuid.uuid4())
        initial_state = make_initial_state(
            symptoms=symptoms,
            patient_age=patient_age,
            patient_sex=patient_sex,
            medical_history=medical_history,
            current_medications=current_medications,
        )

        graph = _get_graph()
        final_state: DiagnosticStateDict = graph.invoke(initial_state)

        _active_sessions[session_id] = final_state
        logger.info(f"[DiagnosticAgent] New session {session_id} started.")
        return _build_response(session_id, final_state)

    def respond(
        self,
        session_id: str,
        clinician_response: str,
    ) -> DiagnosticResponse:
        """
        Process a clinician's follow-up response.
        Runs: refine → END (may mark is_complete=True).
        """
        state = _active_sessions.get(session_id)
        if state is None:
            raise ValueError(f"Session '{session_id}' not found or has expired.")

        if state.get("is_complete"):
            return _build_response(session_id, state)

        # Append clinician response and re-enter the graph at 'refine'
        updated_state: DiagnosticStateDict = {
            **state,
            "clinician_responses": list(state.get("clinician_responses", [])) + [clinician_response],
            "messages": list(state.get("messages", [])) + [
                {"role": "clinician", "content": clinician_response}
            ],
        }

        # Build a mini graph that starts directly at 'refine'
        refine_graph = StateGraph(DiagnosticStateDict)
        refine_graph.add_node("refine", _node_refine)
        refine_graph.set_entry_point("refine")
        refine_graph.add_edge("refine", END)
        compiled_refine = refine_graph.compile()

        final_state: DiagnosticStateDict = compiled_refine.invoke(updated_state)
        _active_sessions[session_id] = final_state

        logger.info(
            f"[DiagnosticAgent] Session {session_id} refined. "
            f"Complete={final_state.get('is_complete')}"
        )
        return _build_response(session_id, final_state)


def get_diagnostic_agent() -> DiagnosticAgent:
    """Get a DiagnosticAgent instance (graph is compiled lazily on first call)."""
    return DiagnosticAgent()
