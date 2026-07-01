"""
LangChain RAG pipeline.

Orchestrates: query → route → retrieve → prompt → generate → cite
Blueprint §5.2 — Online Query & Retrieval Pipeline.
Blueprint §3.1 — Query Analyzer & Router.
"""

import uuid
import time
import logging
from typing import Dict, Any, Optional, Generator

from langchain_core.messages import SystemMessage, HumanMessage

from app.core.llm import get_llm_manager
from app.core.prompts import (
    MEDICAL_RAG_SYSTEM_PROMPT,
    MEDICAL_QUERY_TEMPLATE,
    QUERY_ROUTER_PROMPT,
)
from app.rag.retriever import get_retriever
from app.rag.citations import extract_citations
from app.models.schemas import QueryResponse, Citation, QueryType

logger = logging.getLogger(__name__)


# ─── Query Router ─────────────────────────────────────────────────────────────

def _route_query(query: str, llm_manager) -> QueryType:
    """
    Blueprint §3.1 — Query Analyzer & Router.

    Classifies the incoming query into one of the QueryType categories so
    that the correct retrieval strategy and prompt can be applied.
    Falls back to GENERAL on any classification error.
    """
    try:
        prompt = QUERY_ROUTER_PROMPT.format(query=query)
        messages = [HumanMessage(content=prompt)]
        raw: str = llm_manager.invoke(messages).strip().lower()

        mapping = {
            "general": QueryType.GENERAL,
            "diagnostic": QueryType.DIAGNOSTIC,
            "drug_interaction": QueryType.DRUG_INTERACTION,
            "guideline": QueryType.GUIDELINE,
        }
        query_type = mapping.get(raw, QueryType.GENERAL)
        logger.info(f"[router] Classified query as: {query_type.value!r}")
        return query_type
    except Exception as exc:
        logger.warning(f"[router] Classification failed ({exc}). Defaulting to GENERAL.")
        return QueryType.GENERAL


# ─── RAG Chain ────────────────────────────────────────────────────────────────

class MedicalRAGChain:
    """
    Full RAG chain for medical queries.

    Pipeline (blueprint §5.2):
      1. Route query         — classify intent
      2. Embed & retrieve    — semantic search in vector DB
      3. Construct prompt    — inject context + enforce citation rules
      4. Generate            — LLM synthesis
      5. Extract citations   — map [n] references to source documents
    """

    def __init__(self, n_results: int = 5):
        self.retriever = get_retriever(n_results=n_results)
        self.llm_manager = get_llm_manager()

    def query(
        self,
        query: str,
        query_type: Optional[QueryType] = None,
        max_results: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> QueryResponse:
        """
        Execute a full RAG query pipeline.

        Args:
            query:      Natural language medical query.
            query_type: If None, the router auto-classifies the query.
            max_results: Number of documents to retrieve.
            filters:    Optional metadata filters for retrieval.

        Returns:
            QueryResponse with synthesized answer and citations.
        """
        start_time = time.time()
        query_id = str(uuid.uuid4())

        # Step 1 — Route / classify query (blueprint §3.1)
        if query_type is None:
            query_type = _route_query(query, self.llm_manager)

        # Step 2 — Retrieve relevant documents
        logger.info(f"[{query_id}] Retrieving documents for: '{query[:80]}...'")
        documents = self.retriever.retrieve(
            query=query,
            n_results=max_results,
            filters=filters,
        )

        if not documents:
            processing_time = (time.time() - start_time) * 1000
            return QueryResponse(
                query_id=query_id,
                query=query,
                response=(
                    "I could not find relevant information in the medical knowledge base "
                    "to answer your query. Please try rephrasing your question or ensure "
                    "relevant documents have been ingested into the system.\n\n"
                    "*This information is provided for clinical decision support only.*"
                ),
                citations=[],
                query_type=query_type,
                confidence_score=0.0,
                processing_time_ms=round(processing_time, 2),
            )

        # Step 3 — Format context
        context = self.retriever.format_context(documents)

        # Step 4 — Construct prompt (blueprint §5.2 step 4 — cite sources only)
        user_prompt = MEDICAL_QUERY_TEMPLATE.format(
            context=context,
            query=query,
        )
        messages = [
            SystemMessage(content=MEDICAL_RAG_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        # Step 5 — Generate response
        logger.info(f"[{query_id}] Generating response with {self.llm_manager.provider_display}...")
        response_text = self.llm_manager.invoke(messages)

        # Step 6 — Extract citations
        citations = extract_citations(response_text, documents)

        # Calculate confidence based on relevance scores
        avg_relevance = (
            sum(d["relevance_score"] for d in documents) / len(documents)
            if documents else 0
        )

        processing_time = (time.time() - start_time) * 1000

        logger.info(
            f"[{query_id}] Query complete: type={query_type.value!r}, "
            f"{len(citations)} citations, {processing_time:.0f}ms, "
            f"confidence={avg_relevance:.2f}, provider={self.llm_manager.provider_display}"
        )

        return QueryResponse(
            query_id=query_id,
            query=query,
            response=response_text,
            citations=citations,
            query_type=query_type,
            confidence_score=round(avg_relevance, 4),
            processing_time_ms=round(processing_time, 2),
        )

    def stream_query(
        self,
        query: str,
        query_type: Optional[QueryType] = None,
        max_results: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Generator[str, None, None]:
        """
        Stream a RAG query response for real-time output.
        Routes and retrieves before streaming; yields response chunks.
        """
        # Route
        if query_type is None:
            query_type = _route_query(query, self.llm_manager)

        # Retrieve
        documents = self.retriever.retrieve(
            query=query,
            n_results=max_results,
            filters=filters,
        )

        if not documents:
            yield "No relevant documents found in the knowledge base."
            return

        # Construct prompt
        context = self.retriever.format_context(documents)
        user_prompt = MEDICAL_QUERY_TEMPLATE.format(
            context=context,
            query=query,
        )
        messages = [
            SystemMessage(content=MEDICAL_RAG_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        # Stream response
        for chunk in self.llm_manager.stream(messages):
            yield chunk


def get_rag_chain(n_results: int = 5) -> MedicalRAGChain:
    """Get a configured RAG chain instance."""
    return MedicalRAGChain(n_results=n_results)
