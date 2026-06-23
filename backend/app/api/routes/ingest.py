"""
Data ingestion API routes.
Endpoints for uploading documents and fetching PubMed abstracts.
"""

import time
import logging
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import (
    IngestDocumentRequest, IngestPubMedRequest, IngestResponse
)
from app.models.database import get_db
from app.ingestion.pipeline import get_ingestion_pipeline

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/documents", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: str = Form(...),
    source_url: Optional[str] = Form(None),
):
    """
    Upload and ingest a document into the medical knowledge base.

    Supported types: pdf, csv, json, text
    """
    start_time = time.time()

    # Validate file size (max 50MB)
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")

    if document_type not in ["pdf", "csv", "json", "text"]:
        raise HTTPException(status_code=400, detail=f"Unsupported document type: {document_type}")

    pipeline = get_ingestion_pipeline()
    result = pipeline.ingest_document(
        file_content=content,
        document_type=document_type,
        title=title,
        source_url=source_url,
    )

    processing_time = (time.time() - start_time) * 1000

    return IngestResponse(
        status="success" if not result["errors"] else "partial",
        documents_processed=result["documents_processed"],
        chunks_created=result["chunks_created"],
        errors=result["errors"],
        processing_time_ms=round(processing_time, 2),
    )


@router.post("/pubmed", response_model=IngestResponse)
async def ingest_pubmed(request: IngestPubMedRequest):
    """
    Search PubMed and ingest matching abstracts into the knowledge base.
    """
    start_time = time.time()

    pipeline = get_ingestion_pipeline()
    result = await pipeline.ingest_pubmed(
        query=request.query,
        max_results=request.max_results,
        date_from=request.date_from,
        date_to=request.date_to,
    )

    processing_time = (time.time() - start_time) * 1000

    return IngestResponse(
        status="success" if not result["errors"] else "partial",
        documents_processed=result["documents_processed"],
        chunks_created=result["chunks_created"],
        errors=result["errors"],
        processing_time_ms=round(processing_time, 2),
    )


@router.post("/sample-data", response_model=IngestResponse)
async def ingest_sample_data():
    """
    Load built-in sample medical data for demonstration purposes.
    """
    start_time = time.time()

    pipeline = get_ingestion_pipeline()
    result = pipeline.ingest_sample_data()

    processing_time = (time.time() - start_time) * 1000

    return IngestResponse(
        status="success" if not result["errors"] else "partial",
        documents_processed=result["documents_processed"],
        chunks_created=result["chunks_created"],
        errors=result["errors"],
        processing_time_ms=round(processing_time, 2),
    )


@router.get("/stats")
async def ingestion_stats():
    """Get statistics about the ingested knowledge base."""
    from app.core.vectorstore import get_vectorstore

    vectorstore = get_vectorstore()
    doc_count = vectorstore.count()

    return {
        "total_chunks": doc_count,
        "status": "ready" if doc_count > 0 else "empty",
        "message": (
            f"Knowledge base contains {doc_count} document chunks."
            if doc_count > 0
            else "Knowledge base is empty. Use /api/ingest/sample-data to load demo data."
        ),
    }
