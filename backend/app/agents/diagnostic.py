"""
LangGraph-powered diagnostic assistant agent.
Multi-step workflow for differential diagnosis based on patient symptoms.
"""

import json
import uuid
import logging
from typing import Dict, Any, Optional, List

from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import DiagnosticState
from app.core.llm import get_llm_manager
from app.core.prompts import (
    DIAGNOSTIC_SYSTEM_PROMPT,
    DIAGNOSTIC_GATHERING_TEMPLATE,
    DIAGNOSTIC_REFINEMENT_TEMPLATE,
)
from app.rag.retriever import get_retriever
from app.models.schemas import DiagnosticResponse, Diagnosis, Citation

logger = logging.getLogger(__name__)

# Store active sessions in memory (use Redis in production)
_active_sessions: Dict[str, DiagnosticState] = {}


class DiagnosticAgent:
    """
    LangGraph-style diagnostic agent with multi-step reasoning.

    Workflow:
    1. Information Gathering → query vector DB for symptom-matching conditions
    2. Reasoning → analyze retrieved conditions for differential diagnosis
    3. Refinement → ask follow-up questions to narrow diagnoses
    4. Final Output → ranked diagnoses with supporting evidence
    """

    def __init__(self):
        self.retriever = get_retriever(n_results=8)
        self.llm_manager = get_llm_manager()

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
        Performs initial information gathering and returns first analysis.
        """
        session_id = str(uuid.uuid4())

        state = DiagnosticState(
            symptoms=symptoms,
            patient_age=patient_age,
            patient_sex=patient_sex,
            medical_history=medical_history or [],
            current_medications=current_medications or [],
            stage="gathering",
            iteration=0,
        )

        # Step 1: Information Gathering
        state = self._gather_information(state)

        # Step 2: Initial Reasoning
        state = self._reason(state)

        # Store session
        _active_sessions[session_id] = state

        return self._build_response(session_id, state)

    def respond(
        self,
        session_id: str,
        clinician_response: str,
    ) -> DiagnosticResponse:
        """
        Process a clinician's response to a follow-up question.
        Refines the differential diagnosis based on new information.
        """
        state = _active_sessions.get(session_id)
        if state is None:
            raise ValueError(f"Session {session_id} not found or has expired.")

        if state.is_complete:
            return self._build_response(session_id, state)

        # Record clinician response
        state.clinician_responses.append(clinician_response)
        state.messages.append({"role": "clinician", "content": clinician_response})
        state.iteration += 1

        # Retrieve additional context based on new information
        combined_query = " ".join(state.symptoms) + " " + clinician_response
        documents = self.retriever.retrieve(combined_query, n_results=5)
        additional_context = self.retriever.format_context(documents)

        # Refine diagnosis
        state = self._refine(state, clinician_response, additional_context)

        # Check if we should complete
        if state.iteration >= state.max_iterations:
            state.stage = "complete"
            state.is_complete = True

        # Update session
        _active_sessions[session_id] = state

        return self._build_response(session_id, state)

    def _gather_information(self, state: DiagnosticState) -> DiagnosticState:
        """Node: Retrieve medical literature matching the symptoms."""
        symptom_query = " ".join(state.symptoms)

        if state.medical_history:
            symptom_query += " " + " ".join(state.medical_history)

        documents = self.retriever.retrieve(symptom_query, n_results=8)
        state.retrieved_documents = documents
        state.retrieved_context = self.retriever.format_context(documents)
        state.stage = "reasoning"

        logger.info(f"Gathered {len(documents)} relevant documents for symptoms")
        return state

    def _reason(self, state: DiagnosticState) -> DiagnosticState:
        """Node: Analyze symptoms against retrieved evidence for differential diagnosis."""
        prompt = DIAGNOSTIC_GATHERING_TEMPLATE.format(
            symptoms=", ".join(state.symptoms),
            age=state.patient_age or "Not provided",
            sex=state.patient_sex or "Not provided",
            medical_history=", ".join(state.medical_history) if state.medical_history else "None provided",
            medications=", ".join(state.current_medications) if state.current_medications else "None provided",
            context=state.retrieved_context,
        )

        messages = [
            SystemMessage(content=DIAGNOSTIC_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]

        response = self.llm_manager.invoke(messages)
        state.current_analysis = response
        state.stage = "refining"

        state.messages.append({"role": "agent", "content": response})

        # Extract follow-up question from the response
        state.follow_up_questions = self._extract_follow_up(response)

        logger.info(f"Reasoning complete. Generated {len(state.follow_up_questions)} follow-up questions")
        return state

    def _refine(
        self,
        state: DiagnosticState,
        clinician_response: str,
        additional_context: str,
    ) -> DiagnosticState:
        """Node: Refine differential diagnosis based on clinician's response."""
        prompt = DIAGNOSTIC_REFINEMENT_TEMPLATE.format(
            symptoms=", ".join(state.symptoms),
            age=state.patient_age or "Not provided",
            sex=state.patient_sex or "Not provided",
            medical_history=", ".join(state.medical_history) if state.medical_history else "None provided",
            previous_analysis=state.current_analysis,
            clinician_response=clinician_response,
            context=additional_context,
        )

        messages = [
            SystemMessage(content=DIAGNOSTIC_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]

        response = self.llm_manager.invoke(messages)
        state.current_analysis = response
        state.messages.append({"role": "agent", "content": response})

        # Check if the agent suggests completion or asks more questions
        if state.iteration >= state.max_iterations - 1:
            state.stage = "complete"
            state.is_complete = True
        else:
            state.follow_up_questions = self._extract_follow_up(response)
            if not state.follow_up_questions:
                state.stage = "complete"
                state.is_complete = True

        return state

    def _extract_follow_up(self, response: str) -> List[str]:
        """Extract follow-up questions from the agent's response."""
        questions = []
        lines = response.split("\n")
        for line in lines:
            line = line.strip()
            if line.endswith("?") and len(line) > 15:
                # Clean up the line
                clean = line.lstrip("- •*>1234567890.)")
                if clean.strip():
                    questions.append(clean.strip())

        return questions[:3]  # Max 3 follow-up questions

    def _build_response(
        self,
        session_id: str,
        state: DiagnosticState,
    ) -> DiagnosticResponse:
        """Build the API response from the current state."""
        follow_up = None
        if state.follow_up_questions and not state.is_complete:
            follow_up = state.follow_up_questions[0]

        # Build differential diagnoses from the last analysis
        diagnoses = None
        if state.is_complete or state.stage == "complete":
            diagnoses = self._parse_diagnoses(state.current_analysis)

        return DiagnosticResponse(
            session_id=session_id,
            stage=state.stage,
            message=state.current_analysis,
            follow_up_question=follow_up,
            differential_diagnoses=diagnoses,
            is_complete=state.is_complete,
        )

    def _parse_diagnoses(self, analysis: str) -> List[Diagnosis]:
        """
        Parse the LLM's analysis into structured Diagnosis objects.
        Falls back to a simple extraction if structured parsing fails.
        """
        diagnoses = []

        # Try to extract structured diagnoses from the analysis
        # Look for patterns like "**Condition Name** (Likelihood: High/Medium/Low)"
        import re
        pattern = r'\*\*(.+?)\*\*.*?(?:Likelihood|Probability):\s*(High|Medium|Low)'
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

        # If no structured diagnoses found, create a general one
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


def get_diagnostic_agent() -> DiagnosticAgent:
    """Get a diagnostic agent instance."""
    return DiagnosticAgent()
