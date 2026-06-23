"""
Diagnostic assistant API routes.
Endpoints for the interactive diagnostic workflow.
"""

import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    DiagnosticStartRequest,
    DiagnosticRespondRequest,
    DiagnosticResponse,
)
from app.agents.diagnostic import get_diagnostic_agent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/start", response_model=DiagnosticResponse)
async def start_diagnostic(request: DiagnosticStartRequest):
    """
    Start a new diagnostic session.

    Provide patient symptoms and optional context (age, sex, history).
    The agent will analyze the symptoms, retrieve relevant medical literature,
    and begin the differential diagnosis process.
    """
    try:
        agent = get_diagnostic_agent()

        response = agent.start_session(
            symptoms=request.symptoms,
            patient_age=request.patient_age,
            patient_sex=request.patient_sex,
            medical_history=request.medical_history,
            current_medications=request.current_medications,
        )

        return response

    except RuntimeError as e:
        if "LLM not initialized" in str(e) or "API_KEY" in str(e):
            raise HTTPException(
                status_code=503,
                detail="LLM service not configured. Set GOOGLE_API_KEY (free) in backend/.env",
            )
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Diagnostic start failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start diagnostic: {str(e)}")


@router.post("/respond", response_model=DiagnosticResponse)
async def respond_to_diagnostic(request: DiagnosticRespondRequest):
    """
    Respond to a follow-up question from the diagnostic agent.

    Provide the session ID and your response. The agent will refine
    its differential diagnosis based on the new information.
    """
    try:
        agent = get_diagnostic_agent()

        response = agent.respond(
            session_id=request.session_id,
            clinician_response=request.response,
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Diagnostic respond failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process response: {str(e)}")
