"""
Medical query API routes.
Endpoints for querying the medical knowledge base.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.models.schemas import QueryRequest, QueryResponse, QueryHistoryItem
from app.models.database import get_db, QueryHistory
from app.rag.chain import get_rag_chain

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=QueryResponse)
async def query_knowledge_base(
    request: QueryRequest,
    db: Session = Depends(get_db),
):
    """
    Query the medical knowledge base using natural language.

    Returns a synthesized, evidence-based response with citations to source documents.
    """
    try:
        rag_chain = get_rag_chain(n_results=request.max_results)

        result = rag_chain.query(
            query=request.query,
            query_type=request.query_type,
            max_results=request.max_results,
            filters=request.filters,
        )

        # Save to query history
        try:
            history_entry = QueryHistory(
                id=result.query_id,
                user_id="anonymous",  # Will be updated with auth
                query=request.query,
                response=result.response[:5000],  # Truncate for storage
                query_type=request.query_type.value,
                citation_count=len(result.citations),
                confidence_score=result.confidence_score,
                processing_time_ms=result.processing_time_ms,
            )
            db.add(history_entry)
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to save query history: {e}")

        return result

    except RuntimeError as e:
        if "LLM not initialized" in str(e) or "API_KEY" in str(e):
            raise HTTPException(
                status_code=503,
                detail="LLM service not configured. Set GOOGLE_API_KEY (free) in backend/.env",
            )
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.post("/stream")
async def stream_query(request: QueryRequest):
    """
    Stream a query response for real-time display.
    Returns Server-Sent Events (SSE) with response chunks.
    """
    try:
        rag_chain = get_rag_chain(n_results=request.max_results)

        def generate():
            for chunk in rag_chain.stream_query(
                query=request.query,
                query_type=request.query_type,
                max_results=request.max_results,
                filters=request.filters,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
    except Exception as e:
        logger.error(f"Stream query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_query_history(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Get recent query history."""
    entries = (
        db.query(QueryHistory)
        .order_by(QueryHistory.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        QueryHistoryItem(
            query_id=e.id,
            query=e.query,
            response_preview=e.response[:200] + "..." if len(e.response) > 200 else e.response,
            query_type=e.query_type,
            timestamp=e.created_at,
            citation_count=e.citation_count or 0,
        )
        for e in entries
    ]
