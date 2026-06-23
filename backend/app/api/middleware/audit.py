"""
HIPAA audit logging middleware.
Logs all API access for compliance reporting.
"""

import logging
import time
from datetime import datetime

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.models.database import AuditLog, get_session_factory

logger = logging.getLogger("audit")


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all API requests for HIPAA compliance.
    Records: who, what, when, and from where.
    """

    # Paths to exclude from audit logging
    EXCLUDED_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico", "/"}

    async def dispatch(self, request: Request, call_next):
        # Skip excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        start_time = time.time()

        # Extract user info from token if available
        user_id = "anonymous"
        user_email = "anonymous"

        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from app.api.middleware.auth import decode_token
                payload = decode_token(auth_header[7:])
                user_email = payload.get("sub", "unknown")
                user_id = payload.get("user_id", "unknown")
            except Exception:
                pass

        # Process request
        response = await call_next(request)

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Log to audit trail
        try:
            self._save_audit_log(
                user_id=user_id,
                user_email=user_email,
                action=f"{request.method} {request.url.path}",
                resource=request.url.path,
                details=f"Status: {response.status_code}, Time: {processing_time:.0f}ms",
                ip_address=client_ip,
            )
        except Exception as e:
            logger.warning(f"Failed to save audit log: {e}")

        # Also log to file for immutable audit trail
        logger.info(
            f"AUDIT | User: {user_email} | {request.method} {request.url.path} | "
            f"Status: {response.status_code} | IP: {client_ip} | {processing_time:.0f}ms"
        )

        return response

    def _save_audit_log(
        self,
        user_id: str,
        user_email: str,
        action: str,
        resource: str,
        details: str,
        ip_address: str,
    ):
        """Save audit log entry to the database."""
        SessionLocal = get_session_factory()
        db = SessionLocal()
        try:
            log = AuditLog(
                user_id=user_id,
                user_email=user_email,
                action=action,
                resource=resource,
                details=details,
                ip_address=ip_address,
            )
            db.add(log)
            db.commit()
        except Exception as e:
            logger.error(f"Audit DB write failed: {e}")
        finally:
            db.close()
