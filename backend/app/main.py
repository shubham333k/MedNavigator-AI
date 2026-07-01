"""
FastAPI application entry point.
Healthcare Knowledge Navigator API.
"""

import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.models.database import init_db
from app.models.schemas import HealthResponse
from app.api.routes import auth, query, diagnostic, ingest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    settings = get_settings()
    logger.info("=" * 60)
    logger.info(f"  🏥 {settings.app_name}")
    logger.info(f"  Environment: {settings.app_env}")
    logger.info("=" * 60)

    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    # Initialize database tables
    logger.info("Initializing database...")
    init_db()

    # Seed default admin user
    from app.security.rbac import seed_default_admin
    seed_default_admin()

    logger.info("✅ Application startup complete")
    yield
    logger.info("🛑 Application shutting down")


# ─── Create FastAPI App ──────────────────────────────────

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=(
        "A HIPAA-compliant RAG system for clinicians to query medical literature, "
        "clinical guidelines, and drug databases using natural language."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS Middleware ─────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health Check ─────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """System health check endpoint."""
    services = {
        "database": "healthy",
        "api": "healthy",
    }

    # Check ChromaDB
    try:
        from app.core.vectorstore import get_vectorstore
        vs = get_vectorstore()
        count = vs.count()
        services["vectorstore"] = f"healthy ({count} documents)"
    except Exception as e:
        services["vectorstore"] = f"degraded ({str(e)[:50]})"

    # Check LLM
    try:
        if settings.anthropic_api_key and settings.anthropic_api_key != "":
            services["llm"] = "configured"
        else:
            services["llm"] = "not configured (set ANTHROPIC_API_KEY)"
    except Exception:
        services["llm"] = "error"

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        services=services,
    )


@app.get("/", tags=["System"])
async def root():
    """API root endpoint."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# ─── Register Routers ────────────────────────────────────


app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(query.router, prefix="/api/query", tags=["Medical Queries"])
app.include_router(diagnostic.router, prefix="/api/diagnostic", tags=["Diagnostic Assistant"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["Data Ingestion"])


# ─── Global Exception Handler ────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again.",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
