"""
LangChain RAG pipeline.
Orchestrates query → retrieve → prompt → generate → cite workflow.
"""

import uuid
import time
import logging
from typing import Dict, Any, Optional, Generator

from langchain_core.messages import SystemMessage, HumanMessage

from app.core.llm import get_llm_manager
from app.core.prompts import MEDICAL_RAG_SYSTEM_PROMPT, MEDICAL_QUERY_TEMPLATE
from app.rag.retriever import get_retriever
from app.rag.citations import extract_citations
from app.models.schemas import QueryResponse, Citation, QueryType

logger = logging.getLogger(__name__)


class MedicalRAGChain:
    """
    Full RAG chain for medical queries.
    query → embed → retrieve → construct prompt → generate → extract citations
    """

    def __init__(self, n_results: int = 5):
        self.retriever = get_retriever(n_results=n_results)
        self.llm_manager = get_llm_manager()

    def query(
        self,
        query: str,
        query_type: QueryType = QueryType.GENERAL,
        max_results: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> QueryResponse:
        """
        Execute a full RAG query pipeline.

        Args:
            query: Natural language medical query
            query_type: Type of query for routing
            max_results: Number of documents to retrieve
            filters: Optional metadata filters

        Returns:
            QueryResponse with synthesized answer and citations
        """
        start_time = time.time()
        query_id = str(uuid.uuid4())

        # Step 1: Retrieve relevant documents
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

        # Step 2: Format context
        context = self.retriever.format_context(documents)

        # Step 3: Construct prompt
        user_prompt = MEDICAL_QUERY_TEMPLATE.format(
            context=context,
            query=query,
        )

        messages = [
            SystemMessage(content=MEDICAL_RAG_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        # Step 4: Generate response
        logger.info(f"[{query_id}] Generating response with LLM...")
        response_text = self.llm_manager.invoke(messages)

        # Step 5: Extract citations
        citations = extract_citations(response_text, documents)

        # Calculate confidence based on relevance scores
        avg_relevance = (
            sum(d["relevance_score"] for d in documents) / len(documents)
            if documents else 0
        )

        processing_time = (time.time() - start_time) * 1000

        logger.info(
            f"[{query_id}] Query complete: {len(citations)} citations, "
            f"{processing_time:.0f}ms, confidence={avg_relevance:.2f}"
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
        query_type: QueryType = QueryType.GENERAL,
        max_results: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Generator[str, None, None]:
        """
        Stream a RAG query response for real-time output.
        Yields chunks of the response as they are generated.
        """
        # Retrieve documents
        documents = self.retriever.retrieve(
            query=query,
            n_results=max_results,
            filters=filters,
        )

        if not documents:
            yield "No relevant documents found in the knowledge base."
            return

        # Format context and construct prompt
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
    """Get a configured RAG chain."""
    return MedicalRAGChain(n_results=n_results)
