"""
Custom retriever with semantic search and metadata filtering.
"""

import logging
from typing import List, Dict, Any, Optional

from app.core.vectorstore import get_vectorstore

logger = logging.getLogger(__name__)


class MedicalRetriever:
    """
    Custom retriever that performs semantic search against the medical knowledge base.
    Supports metadata filtering and relevance scoring.
    """

    def __init__(self, n_results: int = 5):
        self.vectorstore = get_vectorstore()
        self.n_results = n_results

    def retrieve(
        self,
        query: str,
        n_results: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a medical query.

        Args:
            query: The natural language query
            n_results: Number of results to return
            filters: ChromaDB where-clause for metadata filtering

        Returns:
            List of retrieved documents with text, metadata, and relevance scores
        """
        k = n_results or self.n_results

        results = self.vectorstore.search(
            query=query,
            n_results=k,
            where=filters,
        )

        documents = []
        if results and results.get("documents"):
            for i, doc_text in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                distance = results["distances"][0][i] if results.get("distances") else 0.0

                # Convert distance to similarity score (ChromaDB uses L2 distance by default)
                # Lower distance = higher relevance
                relevance_score = max(0, 1 - (distance / 2))

                documents.append({
                    "text": doc_text,
                    "metadata": metadata,
                    "relevance_score": round(relevance_score, 4),
                    "source_id": f"doc_{i + 1}",
                })

        # Sort by relevance score (highest first)
        documents.sort(key=lambda x: x["relevance_score"], reverse=True)

        logger.info(f"Retrieved {len(documents)} documents for query: '{query[:80]}...'")
        return documents

    def format_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into a context string for the LLM prompt.
        Each document is labeled with a reference number for citation.
        """
        if not documents:
            return "No relevant documents found in the knowledge base."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            metadata = doc.get("metadata", {})
            title = metadata.get("title", "Unknown Source")
            source_type = metadata.get("source_type", "unknown")
            url = metadata.get("source_url", "")
            score = doc.get("relevance_score", 0)

            header = f"### [Source {i}] {title}"
            if source_type:
                header += f" ({source_type})"

            source_info = f"*Relevance: {score:.0%}*"
            if url:
                source_info += f" | [Link]({url})"

            context_parts.append(
                f"{header}\n{source_info}\n\n{doc['text']}"
            )

        return "\n\n---\n\n".join(context_parts)

    def get_source_list(self, documents: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract a clean list of sources for citation tracking."""
        sources = []
        for i, doc in enumerate(documents, 1):
            metadata = doc.get("metadata", {})
            sources.append({
                "ref_number": i,
                "source_id": doc.get("source_id", f"doc_{i}"),
                "title": metadata.get("title", "Unknown Source"),
                "source_type": metadata.get("source_type", "unknown"),
                "url": metadata.get("source_url", ""),
                "relevance_score": doc.get("relevance_score", 0),
            })
        return sources


def get_retriever(n_results: int = 5) -> MedicalRetriever:
    """Get a configured medical retriever."""
    return MedicalRetriever(n_results=n_results)
