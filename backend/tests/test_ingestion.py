"""
Integration tests for the FastAPI endpoints.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    # Patch external dependencies before importing the app
    with patch("app.core.embeddings.HuggingFaceEmbeddings"), \
         patch("chromadb.HttpClient"), \
         patch("chromadb.PersistentClient"):
        from app.main import app
        with TestClient(app) as c:
            yield c


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "services" in data


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "Healthcare" in data["name"]


def test_login_default_admin(client):
    """Test login with default admin credentials."""
    response = client.post("/api/auth/login", json={
        "email": "admin@healthcare.nav",
        "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_ingest_stats_endpoint(client):
    """Test the ingestion stats endpoint."""
    with patch("app.core.vectorstore.VectorStoreManager.count", return_value=42):
        response = client.get("/api/ingest/stats")
        assert response.status_code == 200


def test_register_user(client):
    """Test user registration."""
    import uuid
    email = f"testclinician_{uuid.uuid4().hex[:8]}@hospital.org"
    response = client.post("/api/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "Test Clinician",
        "role": "clinician",
        "specialty": "Cardiology"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["role"] == "clinician"
