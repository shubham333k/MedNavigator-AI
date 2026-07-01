"""
Text chunking strategies for medical documents.

Blueprint §5.1 (Data Ingestion Pipeline) specifies:
  - LangChain ``RecursiveCharacterTextSplitter``           ✅ implemented
  - Chunk size: 500-1000 tokens, respecting semantic boundaries  ✅ default=800
  - Chunk overlap to preserve context across boundaries    ✅ default=200

The separator list is ordered by priority from coarse (section headers) to
fine (word breaks), ensuring medical section structure is preserved.
"""

import logging
from typing import List, Dict, Any, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class MedicalTextChunker:
    """
    Medical-aware text chunking.
    Respects section boundaries commonly found in medical literature.
    """

    # Medical document section separators (ordered by priority)
    MEDICAL_SEPARATORS = [
        "\n## ",        # Markdown H2 sections
        "\n### ",       # Markdown H3 sections
        "\n\n---\n\n",  # Section dividers
        "\n\n\n",       # Triple newlines (major section breaks)
        "\n\n",         # Double newlines (paragraph breaks)
        "\n",           # Single newlines
        ". ",           # Sentence boundaries
        " ",            # Word boundaries
    ]

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or self.MEDICAL_SEPARATORS

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len,
            is_separator_regex=False,
        )

    def chunk_text(
        self,
        text: str,
        base_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Split text into chunks with metadata.

        Returns a list of dicts with 'text' and 'metadata' keys.
        """
        if not text or not text.strip():
            return []

        base_metadata = base_metadata or {}

        # Create LangChain documents
        chunks = self.splitter.split_text(text)

        result = []
        for i, chunk_text in enumerate(chunks):
            if not chunk_text.strip():
                continue

            chunk_metadata = {
                **base_metadata,
                "chunk_index": i,
                "chunk_total": len(chunks),
                "chunk_size": len(chunk_text),
            }

            result.append({
                "text": chunk_text.strip(),
                "metadata": chunk_metadata,
            })

        logger.info(
            f"Chunked text into {len(result)} chunks "
            f"(chunk_size={self.chunk_size}, overlap={self.chunk_overlap})"
        )

        return result


def get_chunker(
    chunk_size: int = 800,
    chunk_overlap: int = 200,
) -> MedicalTextChunker:
    """Get a configured medical text chunker."""
    return MedicalTextChunker(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
