"""
Database models and session management using SQLAlchemy.
SQLite for user management, query history, and audit logs.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Text, Float, Integer, Boolean,
    create_engine, event
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import get_settings

Base = declarative_base()


def generate_uuid() -> str:
    return str(uuid.uuid4())


# ─── User Model ───────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False, default="clinician")
    specialty = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ─── Query History Model ─────────────────────────────────

class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    query_type = Column(String, nullable=False, default="general")
    citation_count = Column(Integer, default=0)
    confidence_score = Column(Float, nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ─── Diagnostic Session Model ────────────────────────────

class DiagnosticSession(Base):
    __tablename__ = "diagnostic_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    symptoms = Column(Text, nullable=False)
    patient_age = Column(Integer, nullable=True)
    patient_sex = Column(String, nullable=True)
    medical_history = Column(Text, nullable=True)
    current_stage = Column(String, default="gathering")
    conversation_state = Column(Text, nullable=True)
    final_diagnoses = Column(Text, nullable=True)
    is_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ─── Audit Log Model ─────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    user_email = Column(String, nullable=False)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


# ─── Ingested Document Tracking ──────────────────────────

class IngestedDocument(Base):
    __tablename__ = "ingested_documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    chunk_count = Column(Integer, default=0)
    file_hash = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)
    ingested_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ─── Database Engine & Session ────────────────────────────

def get_engine():
    settings = get_settings()
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},  # SQLite specific
        echo=settings.debug,
    )

    # Enable WAL mode for SQLite (better concurrent reads)
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def get_session_factory():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all database tables."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Dependency for FastAPI route injection."""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
