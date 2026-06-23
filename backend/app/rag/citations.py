"""
Citation extraction and formatting utilities.
Maps LLM response references back to source documents.
"""

import re
import logging
from typing import List, Dict, Any

from app.models.schemas import Citation

logger = logging.getLogger(__name__)


def extract_citations(
    response_text: str,
    source_documents: List[Dict[str, Any]],
) -> List[Citation]:
    """
    Extract citation references from LLM response and map to source documents.

    The LLM is prompted to use [1], [2], etc. format for citations.
    This function maps those references to the actual source documents.
    """
    # Find all citation references in the response text (e.g., [1], [2], [1,2], [1-3])
    citation_refs = set()

    # Match patterns like [1], [2], [1, 2], [1-3]
    single_refs = re.findall(r'\[(\d+)\]', response_text)
    for ref in single_refs:
        citation_refs.add(int(ref))

    # Match range patterns like [1-3]
    range_refs = re.findall(r'\[(\d+)-(\d+)\]', response_text)
    for start, end in range_refs:
        for i in range(int(start), int(end) + 1):
            citation_refs.add(i)

    citations = []
    for ref_num in sorted(citation_refs):
        # Map to source document (1-indexed)
        doc_index = ref_num - 1
        if 0 <= doc_index < len(source_documents):
            doc = source_documents[doc_index]
            metadata = doc.get("metadata", {})

            citation = Citation(
                source_id=doc.get("source_id", f"doc_{ref_num}"),
                title=metadata.get("title", "Unknown Source"),
                source_type=metadata.get("source_type", "unknown"),
                authors=metadata.get("authors"),
                publication_date=metadata.get("publication_date"),
                url=metadata.get("source_url"),
                relevance_score=doc.get("relevance_score", 0.0),
                snippet=doc.get("text", "")[:300] + "...",
            )
            citations.append(citation)
        else:
            logger.warning(f"Citation [{ref_num}] references non-existent document (only {len(source_documents)} available)")

    logger.info(f"Extracted {len(citations)} citations from response")
    return citations


def format_citations_for_display(citations: List[Citation]) -> str:
    """
    Format citations into a readable markdown references section.
    """
    if not citations:
        return ""

    lines = ["## References\n"]
    for i, citation in enumerate(citations, 1):
        line = f"**[{i}]** {citation.title}"
        if citation.authors:
            line += f" — {citation.authors}"
        if citation.publication_date:
            line += f" ({citation.publication_date})"
        if citation.url:
            line += f" [Link]({citation.url})"
        lines.append(line)

    return "\n".join(lines)
