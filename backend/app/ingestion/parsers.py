"""
Document parsers for various file formats.
Extracts text from PDFs, CSVs, JSON, and plain text files.
"""

import logging
import csv
import json
from io import BytesIO, StringIO
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ParsedDocument:
    """Represents a parsed document with text and metadata."""

    def __init__(
        self,
        text: str,
        title: str,
        source_type: str,
        source_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.text = text
        self.title = title
        self.source_type = source_type
        self.source_url = source_url
        self.metadata = metadata or {}


def parse_pdf(file_content: bytes, title: str, source_url: Optional[str] = None) -> ParsedDocument:
    """Parse a PDF file and extract text content."""
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(BytesIO(file_content))
        pages_text = []

        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                pages_text.append(text.strip())

        full_text = "\n\n".join(pages_text)

        if not full_text.strip():
            raise ValueError("No text could be extracted from the PDF")

        logger.info(f"Parsed PDF '{title}': {len(reader.pages)} pages, {len(full_text)} chars")

        return ParsedDocument(
            text=full_text,
            title=title,
            source_type="pdf",
            source_url=source_url,
            metadata={
                "page_count": len(reader.pages),
                "char_count": len(full_text),
            },
        )
    except ImportError:
        raise RuntimeError("PyPDF2 is required for PDF parsing. Install it with: pip install pypdf2")


def parse_csv(file_content: bytes, title: str, source_url: Optional[str] = None) -> ParsedDocument:
    """Parse a CSV file into structured text (e.g., drug interaction databases)."""
    text_content = file_content.decode("utf-8")
    reader = csv.DictReader(StringIO(text_content))

    rows = list(reader)
    if not rows:
        raise ValueError("CSV file is empty")

    # Convert each row into a readable text entry
    entries = []
    for row in rows:
        entry_parts = [f"**{key}**: {value}" for key, value in row.items() if value]
        entries.append("\n".join(entry_parts))

    full_text = "\n\n---\n\n".join(entries)

    logger.info(f"Parsed CSV '{title}': {len(rows)} rows")

    return ParsedDocument(
        text=full_text,
        title=title,
        source_type="csv",
        source_url=source_url,
        metadata={
            "row_count": len(rows),
            "columns": list(rows[0].keys()) if rows else [],
        },
    )


def parse_json(file_content: bytes, title: str, source_url: Optional[str] = None) -> ParsedDocument:
    """Parse a JSON file into structured text."""
    data = json.loads(file_content.decode("utf-8"))

    if isinstance(data, list):
        entries = []
        for item in data:
            if isinstance(item, dict):
                entry_parts = [f"**{key}**: {value}" for key, value in item.items()]
                entries.append("\n".join(entry_parts))
            else:
                entries.append(str(item))
        full_text = "\n\n---\n\n".join(entries)
    elif isinstance(data, dict):
        entry_parts = [f"**{key}**: {json.dumps(value, indent=2) if isinstance(value, (dict, list)) else value}"
                       for key, value in data.items()]
        full_text = "\n".join(entry_parts)
    else:
        full_text = str(data)

    logger.info(f"Parsed JSON '{title}': {len(full_text)} chars")

    return ParsedDocument(
        text=full_text,
        title=title,
        source_type="json",
        source_url=source_url,
        metadata={"format": "json"},
    )


def parse_text(file_content: bytes, title: str, source_url: Optional[str] = None) -> ParsedDocument:
    """Parse a plain text file."""
    text = file_content.decode("utf-8")

    logger.info(f"Parsed text '{title}': {len(text)} chars")

    return ParsedDocument(
        text=text,
        title=title,
        source_type="text",
        source_url=source_url,
        metadata={"char_count": len(text)},
    )


def parse_document(
    file_content: bytes,
    document_type: str,
    title: str,
    source_url: Optional[str] = None,
) -> ParsedDocument:
    """Route document parsing to the appropriate parser."""
    parsers = {
        "pdf": parse_pdf,
        "csv": parse_csv,
        "json": parse_json,
        "text": parse_text,
    }

    parser = parsers.get(document_type.lower())
    if parser is None:
        raise ValueError(f"Unsupported document type: {document_type}. Supported: {list(parsers.keys())}")

    return parser(file_content, title, source_url)
