"""
Application configuration management.
Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = Field(default="Healthcare Knowledge Navigator")
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)
    backend_host: str = Field(default="0.0.0.0")
    backend_port: int = Field(default=8000)
    frontend_url: str = Field(default="http://localhost:3000")
    backend_url: str = Field(default="http://localhost:8000")

    # Google Gemini (free tier — preferred)
    google_api_key: str = Field(default="")

    # OpenAI (fallback)
    openai_api_key: str = Field(default="")

    # Anthropic (fallback)
    anthropic_api_key: str = Field(default="")

    # Embedding Model
    embedding_model: str = Field(default="BAAI/bge-large-en-v1.5")

    # ChromaDB
    chroma_host: str = Field(default="localhost")
    chroma_port: int = Field(default=8100)
    chroma_collection: str = Field(default="medical_knowledge")

    # JWT Security
    jwt_secret_key: str = Field(default="dev-secret-key-change-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_days: int = Field(default=7)

    # Encryption
    encryption_key: Optional[str] = Field(default=None)

    # PubMed
    ncbi_api_key: Optional[str] = Field(default=None)
    ncbi_email: str = Field(default="user@example.com")

    # Database
    database_url: str = Field(default="sqlite:///./healthcare_navigator.db")

    # Logging
    log_level: str = Field(default="INFO")
    audit_log_file: str = Field(default="logs/audit.log")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
