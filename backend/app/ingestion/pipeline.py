"""
Data ingestion pipeline orchestrator.
Coordinates parsing, chunking, embedding, and indexing of medical documents.
"""

import uuid
import hashlib
import json
import logging
from typing import List, Dict, Any, Optional

from app.core.vectorstore import get_vectorstore
from app.ingestion.parsers import ParsedDocument, parse_document
from app.ingestion.chunker import get_chunker
from app.ingestion.pubmed import get_pubmed_fetcher
from app.models.database import IngestedDocument, get_session_factory

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Orchestrates the full document ingestion workflow."""

    def __init__(self):
        self.vectorstore = get_vectorstore()
        self.chunker = get_chunker(chunk_size=800, chunk_overlap=200)

    def _generate_doc_id(self, title: str, content_hash: str) -> str:
        """Generate a deterministic document ID."""
        return hashlib.md5(f"{title}:{content_hash}".encode()).hexdigest()

    def _compute_hash(self, content: bytes) -> str:
        """Compute a hash for deduplication."""
        return hashlib.sha256(content).hexdigest()

    def ingest_document(
        self,
        file_content: bytes,
        document_type: str,
        title: str,
        source_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Ingest a document: parse → chunk → embed → store.

        Returns:
            Dict with processing results (chunks_created, errors, etc.)
        """
        errors = []
        content_hash = self._compute_hash(file_content)

        # Step 1: Parse document
        try:
            parsed = parse_document(file_content, document_type, title, source_url)
        except Exception as e:
            logger.error(f"Failed to parse document '{title}': {e}")
            return {"documents_processed": 0, "chunks_created": 0, "errors": [str(e)]}

        # Step 2: Chunk text
        base_metadata = {
            "title": title,
            "source_type": document_type,
            "source_url": source_url or "",
            "content_hash": content_hash,
            **(metadata or {}),
            **(parsed.metadata or {}),
        }

        chunks = self.chunker.chunk_text(parsed.text, base_metadata)

        if not chunks:
            return {"documents_processed": 1, "chunks_created": 0, "errors": ["No chunks generated"]}

        # Step 3: Store in vector database
        chunk_texts = [c["text"] for c in chunks]
        chunk_metadatas = [c["metadata"] for c in chunks]
        chunk_ids = [
            f"{self._generate_doc_id(title, content_hash)}_{i}"
            for i in range(len(chunks))
        ]

        try:
            self.vectorstore.add_documents(
                texts=chunk_texts,
                metadatas=chunk_metadatas,
                ids=chunk_ids,
            )
        except Exception as e:
            logger.error(f"Failed to store chunks in vector DB: {e}")
            errors.append(f"Vector store error: {str(e)}")

        # Step 4: Track in database
        try:
            self._track_ingestion(
                title=title,
                source_type=document_type,
                source_url=source_url,
                chunk_count=len(chunks),
                content_hash=content_hash,
                metadata=metadata,
                user_id=user_id,
            )
        except Exception as e:
            logger.warning(f"Failed to track ingestion: {e}")

        logger.info(f"✅ Ingested '{title}': {len(chunks)} chunks created")

        return {
            "documents_processed": 1,
            "chunks_created": len(chunks),
            "errors": errors,
        }

    async def ingest_pubmed(
        self,
        query: str,
        max_results: int = 10,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Ingest PubMed abstracts based on a search query.
        """
        fetcher = get_pubmed_fetcher()
        articles = await fetcher.search_and_fetch(query, max_results, date_from, date_to)

        total_chunks = 0
        errors = []

        for article in articles:
            # Combine title and abstract for richer content
            full_text = f"# {article['title']}\n\n"
            if article.get("authors"):
                full_text += f"**Authors**: {article['authors']}\n"
            if article.get("journal"):
                full_text += f"**Journal**: {article['journal']}\n"
            if article.get("publication_date"):
                full_text += f"**Date**: {article['publication_date']}\n"
            full_text += f"\n{article.get('abstract', '')}"

            content_bytes = full_text.encode("utf-8")

            result = self.ingest_document(
                file_content=content_bytes,
                document_type="pubmed",
                title=article["title"],
                source_url=article.get("url"),
                metadata={
                    "pmid": article.get("pmid", ""),
                    "authors": article.get("authors", ""),
                    "journal": article.get("journal", ""),
                    "publication_date": article.get("publication_date", ""),
                },
                user_id=user_id,
            )

            total_chunks += result["chunks_created"]
            errors.extend(result["errors"])

        return {
            "documents_processed": len(articles),
            "chunks_created": total_chunks,
            "errors": errors,
        }

    def _track_ingestion(
        self,
        title: str,
        source_type: str,
        source_url: Optional[str],
        chunk_count: int,
        content_hash: str,
        metadata: Optional[Dict],
        user_id: Optional[str],
    ):
        """Record ingestion in the tracking database."""
        SessionLocal = get_session_factory()
        db = SessionLocal()
        try:
            doc = IngestedDocument(
                title=title,
                source_type=source_type,
                source_url=source_url,
                chunk_count=chunk_count,
                file_hash=content_hash,
                metadata_json=json.dumps(metadata) if metadata else None,
                ingested_by=user_id,
            )
            db.add(doc)
            db.commit()
        finally:
            db.close()

    def ingest_sample_data(self) -> Dict[str, Any]:
        """Ingest built-in sample medical data for demonstration."""
        from app.data.sample_data import SAMPLE_MEDICAL_DOCUMENTS

        total_chunks = 0
        total_docs = 0
        errors = []

        for doc in SAMPLE_MEDICAL_DOCUMENTS:
            result = self.ingest_document(
                file_content=doc["content"].encode("utf-8"),
                document_type="text",
                title=doc["title"],
                source_url=doc.get("url"),
                metadata=doc.get("metadata", {}),
            )
            total_docs += result["documents_processed"]
            total_chunks += result["chunks_created"]
            errors.extend(result["errors"])

        logger.info(f"✅ Ingested {total_docs} sample documents ({total_chunks} chunks)")
        return {
            "documents_processed": total_docs,
            "chunks_created": total_chunks,
            "errors": errors,
        }


def get_ingestion_pipeline() -> IngestionPipeline:
    """Get an ingestion pipeline instance."""
    return IngestionPipeline()
