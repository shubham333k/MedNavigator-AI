"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ─── Enums ────────────────────────────────────────────────

class UserRole(str, Enum):
    """
    Blueprint §6.2 — Role-Based Access Control.
    Three roles: Admin (full access), Clinician (query + diagnose), Viewer (read-only).
    """
    ADMIN = "admin"
    CLINICIAN = "clinician"
    VIEWER = "viewer"          # replaces the former 'researcher' role


class QueryType(str, Enum):
    GENERAL = "general"
    DIAGNOSTIC = "diagnostic"
    DRUG_INTERACTION = "drug_interaction"
    GUIDELINE = "guideline"


class DocumentType(str, Enum):
    PDF = "pdf"
    PUBMED = "pubmed"
    CSV = "csv"
    JSON = "json"
    TEXT = "text"


# ─── Auth Schemas ─────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: UserRole = UserRole.CLINICIAN
    specialty: Optional[str] = None


# ─── User Schemas ─────────────────────────────────────────

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    specialty: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Query Schemas ────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000, description="Natural language medical query")
    query_type: QueryType = Field(default=QueryType.GENERAL)
    max_results: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")
    filters: Optional[dict] = Field(default=None, description="Metadata filters for retrieval")


class Citation(BaseModel):
    source_id: str
    title: str
    source_type: str
    authors: Optional[str] = None
    publication_date: Optional[str] = None
    url: Optional[str] = None
    relevance_score: float
    snippet: str = Field(description="Relevant excerpt from the source")


class QueryResponse(BaseModel):
    query_id: str
    query: str
    response: str = Field(description="Synthesized response with inline citations")
    citations: List[Citation] = Field(default_factory=list)
    query_type: QueryType
    confidence_score: Optional[float] = None
    processing_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class QueryHistoryItem(BaseModel):
    query_id: str
    query: str
    response_preview: str
    query_type: QueryType
    timestamp: datetime
    citation_count: int


# ─── Diagnostic Schemas ──────────────────────────────────

class DiagnosticStartRequest(BaseModel):
    symptoms: List[str] = Field(..., min_length=1, description="List of patient symptoms")
    patient_age: Optional[int] = Field(default=None, ge=0, le=150)
    patient_sex: Optional[str] = Field(default=None, pattern="^(male|female|other)$")
    medical_history: Optional[List[str]] = Field(default=None, description="Relevant medical history (de-identified)")
    current_medications: Optional[List[str]] = Field(default=None)


class DiagnosticRespondRequest(BaseModel):
    session_id: str = Field(..., description="Active diagnostic session ID")
    response: str = Field(..., description="Clinician's response to follow-up question")


class Diagnosis(BaseModel):
    condition: str
    likelihood: str = Field(description="High, Medium, or Low")
    confidence_score: float = Field(ge=0.0, le=1.0)
    supporting_evidence: List[str]
    recommended_tests: Optional[List[str]] = None
    citations: List[Citation] = Field(default_factory=list)


class DiagnosticResponse(BaseModel):
    session_id: str
    stage: str = Field(description="Current stage: gathering, reasoning, refining, complete")
    message: str = Field(description="Agent message to the clinician")
    follow_up_question: Optional[str] = None
    differential_diagnoses: Optional[List[Diagnosis]] = None
    is_complete: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ─── Ingestion Schemas ───────────────────────────────────

class IngestDocumentRequest(BaseModel):
    document_type: DocumentType
    title: str
    source_url: Optional[str] = None
    metadata: Optional[dict] = Field(default=None, description="Additional metadata for the document")


class IngestPubMedRequest(BaseModel):
    query: str = Field(..., description="PubMed search query")
    max_results: int = Field(default=10, ge=1, le=100)
    date_from: Optional[str] = Field(default=None, description="Start date (YYYY/MM/DD)")
    date_to: Optional[str] = Field(default=None, description="End date (YYYY/MM/DD)")


class IngestResponse(BaseModel):
    status: str
    documents_processed: int
    chunks_created: int
    errors: List[str] = Field(default_factory=list)
    processing_time_ms: float


# ─── Audit Schemas ────────────────────────────────────────

class AuditLogEntry(BaseModel):
    id: str
    user_id: str
    user_email: str
    action: str
    resource: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


# ─── Health Check ─────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict
