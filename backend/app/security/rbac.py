"""
Role-Based Access Control (RBAC) for the Healthcare Knowledge Navigator.

Blueprint §6.2 defines three roles:
  Admin     — full system access including ingestion, user management, audit logs
  Clinician — can query knowledge base and run diagnostic assistant
  Viewer    — read-only query access (replaces the old 'researcher' role)

Manages user roles, permissions, and default admin seeding.
"""

import logging
from typing import Optional, List

import bcrypt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.database import User, get_session_factory

logger = logging.getLogger(__name__)

ROLE_PERMISSIONS = {
    "admin": {
        "can_query": True,
        "can_diagnose": True,
        "can_ingest": True,
        "can_manage_users": True,
        "can_view_audit_logs": True,
        "can_delete_data": True,
    },
    "clinician": {
        "can_query": True,
        "can_diagnose": True,
        "can_ingest": False,
        "can_manage_users": False,
        "can_view_audit_logs": False,
        "can_delete_data": False,
    },
    # Blueprint §6.2 — Viewer: read-only knowledge base access
    "viewer": {
        "can_query": True,
        "can_diagnose": False,
        "can_ingest": False,
        "can_manage_users": False,
        "can_view_audit_logs": False,
        "can_delete_data": False,
    },
}


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def check_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission."""
    role_perms = ROLE_PERMISSIONS.get(role, {})
    return role_perms.get(permission, False)


def get_user_by_email(email: str) -> Optional[User]:
    """Look up a user by email."""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()


def create_user(
    email: str,
    password: str,
    full_name: str,
    role: str = "clinician",
    specialty: Optional[str] = None,
) -> User:
    """Create a new user."""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=role,
            specialty=specialty,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created user: {email} (role: {role})")
        return user
    finally:
        db.close()


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user with email and password."""
    user = get_user_by_email(email)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def seed_default_admin():
    """Create a default admin user if none exists."""
    existing = get_user_by_email("admin@healthcare.nav")
    if existing is None:
        create_user(
            email="admin@healthcare.nav",
            password="admin123",
            full_name="System Administrator",
            role="admin",
        )
        logger.info("✅ Default admin user created (admin@healthcare.nav / admin123)")
    else:
        logger.info("Default admin user already exists")
