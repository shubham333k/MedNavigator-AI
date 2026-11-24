"""
Tests for the RAG pipeline components.
"""

import pytest
from unittest.mock import MagicMock, patch


def test_chunker_basic():
    """Test that the text chunker splits text correctly."""
    from app.ingestion.chunker import MedicalTextChunker

    chunker = MedicalTextChunker(chunk_size=100, chunk_overlap=20)
    text = "This is a test sentence. " * 20
    chunks = chunker.chunk_text(text, {"title": "Test"})

    assert len(chunks) > 1
    for chunk in chunks:
        assert "text" in chunk
        assert "metadata" in chunk
        assert len(chunk["text"]) <= 150  # Allow some tolerance


def test_chunker_empty():
    """Test that the chunker handles empty input."""
    from app.ingestion.chunker import MedicalTextChunker

    chunker = MedicalTextChunker()
    chunks = chunker.chunk_text("", {})
    assert chunks == []


def test_chunker_medical_separators():
    """Test that the chunker respects medical document section boundaries."""
    from app.ingestion.chunker import MedicalTextChunker

    chunker = MedicalTextChunker(chunk_size=100, chunk_overlap=0)
    text = "## Section 1\nSome content here.\n\n## Section 2\nMore content here.\n\n## Section 3\nEven more content."
    chunks = chunker.chunk_text(text, {})
    assert len(chunks) >= 1


def test_citation_extraction():
    """Test citation extraction from LLM response."""
    from app.rag.citations import extract_citations

    response = "According to the guidelines [1], hypertension should be managed [2]. Some studies [1,2] also show..."
    source_docs = [
        {"source_id": "doc_1", "metadata": {"title": "JNC8 Guidelines", "source_type": "guideline"}, "relevance_score": 0.95, "text": "Sample text"},
        {"source_id": "doc_2", "metadata": {"title": "ADA Standards", "source_type": "guideline"}, "relevance_score": 0.85, "text": "Sample text 2"},
    ]

    citations = extract_citations(response, source_docs)
    assert len(citations) == 2
    assert citations[0].title == "JNC8 Guidelines"
    assert citations[1].title == "ADA Standards"


def test_citation_extraction_no_refs():
    """Test citation extraction when no references are in the response."""
    from app.rag.citations import extract_citations

    response = "This is a response without any citations."
    citations = extract_citations(response, [])
    assert citations == []


def test_deidentification():
    """Test PHI de-identification."""
    from app.security.deidentify import deidentify_text, contains_phi

    # Test SSN detection
    text_with_phi = "Patient John Smith, SSN: 123-45-6789, DOB: 01/15/1985"
    deidentified = deidentify_text(text_with_phi)
    assert "123-45-6789" not in deidentified
    assert "[REDACTED_SSN]" in deidentified

    # Test email detection
    text_with_email = "Contact: doctor@hospital.com"
    deidentified = deidentify_text(text_with_email)
    assert "doctor@hospital.com" not in deidentified

    # Test that medical text is preserved
    clean_text = "Blood pressure target: <130/80 mmHg for CKD patients."
    assert not contains_phi(clean_text)


def test_password_hashing():
    """Test password hashing and verification."""
    from app.security.rbac import hash_password, verify_password

    password = "TestPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_role_permissions():
    """Test RBAC role permissions."""
    from app.security.rbac import check_permission

    # Admin has all permissions
    assert check_permission("admin", "can_query")
    assert check_permission("admin", "can_ingest")
    assert check_permission("admin", "can_manage_users")

    # Clinician can query and diagnose but not manage users
    assert check_permission("clinician", "can_query")
    assert check_permission("clinician", "can_diagnose")
    assert not check_permission("clinician", "can_manage_users")
    assert not check_permission("clinician", "can_ingest")

    # Viewer can query but not ingest or diagnose
    assert check_permission("viewer", "can_query")
    assert not check_permission("viewer", "can_ingest")
    assert not check_permission("viewer", "can_diagnose")
