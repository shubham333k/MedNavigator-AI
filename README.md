# MedNavigator-AI

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.165-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-3.5%20Flash%20Lite-FF6D00?logo=google&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-vector%20store-FF4B4B)
![License](https://img.shields.io/badge/License-MIT-green)

**An evidence-grounded clinical knowledge navigator powered by RAG.**

Query medical references, ingest documents, retrieve citations, and explore a LangGraph diagnostic workflow through a FastAPI backend and Next.js frontend.

</div>

## Overview

MedNavigator-AI combines local document embeddings, ChromaDB retrieval, and Google Gemini generation to produce medical knowledge responses grounded in ingested sources. It includes JWT authentication, role-based access control, audit logging, PHI de-identification utilities, document ingestion, PubMed integration, and a browser-based interface.

> This is an educational project with HIPAA-aligned security controls. It is not HIPAA-certified, a medical device, or a substitute for professional medical advice.

## Features

- Natural-language medical queries with source citations
- PDF, text, CSV, JSON, sample-data, and PubMed ingestion
- Local BGE embeddings with CPU fallback and configurable model selection
- ChromaDB persistent vector storage
- Gemini Flash LLM integration with configurable model selection
- JWT access/refresh tokens and Admin, Clinician, and Viewer roles
- LangGraph diagnostic assistant workflow
- Next.js 14 frontend with automatic JWT refresh and login redirect
- SQLite persistence for users, query history, audit records, and ingestion metadata
- Docker Compose and GitHub Actions configuration

## Architecture

~~~~text
Next.js frontend
        |
        | REST + JWT
        v
FastAPI backend ---- SQLite
        |
        +---- ChromaDB <---- BGE embeddings
        |
        +---- Google Gemini
~~~~

## Project structure

~~~~text
backend/
  app/
    api/          API routes and authentication middleware
    agents/       LangGraph diagnostic workflow
    core/         settings, embeddings, LLM, and vector store
    ingestion/    parsers, chunking, PubMed, and pipeline orchestration
    models/       SQLAlchemy and Pydantic models
    rag/          retrieval, generation, and citations
    security/     RBAC, encryption, and de-identification utilities
  scripts/        local seed scripts
  sample_data/    small text and PDF fixtures
  tests/          backend tests
frontend/
  src/app/        Next.js pages
  src/components/ reusable UI components
  src/lib/        API client and auth helpers
docker-compose.yml
~~~~

## Requirements

- Python 3.12 recommended
- Node.js 20+
- npm
- Google Gemini API key for generated answers
- Docker Desktop only if using the Docker workflow

## Local development

### 1. Configure the backend

From the repository root, copy the template into the backend directory:

~~~~powershell
Copy-Item .env.example backend/.env
~~~~

Edit 'backend/.env' and set at least:

~~~~env
GOOGLE_API_KEY=your_google_ai_studio_key
JWT_SECRET_KEY=replace-with-a-long-random-secret
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
GEMINI_MODEL=gemini-3.5-flash-lite
CHROMA_DATA_PATH=./chroma_data
~~~~

Keep secrets in '.env' files only. Never commit them.

### 2. Start the backend

~~~~powershell
cd backend
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
~~~~

The API is available at http://localhost:8000, with Swagger at http://localhost:8000/docs.

The application seeds this local admin account on startup if it does not already exist:

~~~~text
Email:    admin@healthcare.nav
Password: admin123
~~~~

Change the password before any non-local deployment.

### 3. Seed sample documents

Stop the backend before running a separate seed process so two processes do not write to the same local Chroma store.

~~~~powershell
cd backend
./venv/Scripts/Activate.ps1
python scripts/seed_sample_data.py
~~~~

The first run downloads 'BAAI/bge-small-en-v1.5'; this is expected and the model is cached locally.

### 4. Start the frontend

Create 'frontend/.env.local':

~~~~env
NEXT_PUBLIC_API_URL=http://localhost:8000
~~~~

Then run:

~~~~powershell
cd frontend
npm install
npm run dev
~~~~

Open http://localhost:3000, sign in with the local admin account, and use Query, Knowledge Base, or Diagnostic Assistant.

Do not run 'npm run build' at the same time as 'npm run dev'; both use '.next' and can cause temporary asset 404s.

## API overview

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| GET | /health | Service health | No |
| POST | /api/auth/login | Create access and refresh tokens | No |
| POST | /api/auth/refresh | Refresh an access token | No |
| POST | /api/query/ | Run a cited RAG query | Yes |
| POST | /api/ingest/upload | Upload and ingest a document | Admin |
| POST | /api/ingest/pubmed | Fetch PubMed abstracts | Admin |
| POST | /api/ingest/sample-data | Load built-in sample data | Admin |
| POST | /api/diagnostic/start | Start diagnostic workflow | Yes |
| POST | /api/diagnostic/respond | Continue diagnostic workflow | Yes |

## Docker

Configure the root '.env' from '.env.example' for Compose, then run:

~~~~powershell
docker compose up --build
~~~~

The frontend is served at port 3000, the API at port 8000, and ChromaDB at port 8100.

## Testing

Backend:

~~~~powershell
cd backend
./venv/Scripts/Activate.ps1
pytest tests -v
~~~~

Frontend:

~~~~powershell
cd frontend
npm run type-check
npm run build
~~~~

## Troubleshooting

- 'Authentication required': sign in first. The frontend redirects to '/login' when the access token is missing or expired.
- 'NOT_FOUND' for a Gemini model: use 'GEMINI_MODEL=gemini-3.5-flash-lite' and restart Uvicorn.
- '503 UNAVAILABLE' from Gemini: retry after a short wait or choose another available Gemini Flash model.
- 'Error creating hnsw segment reader: Nothing found on disk': stop the backend before seeding, remove 'backend/chroma_data', seed again, and restart the backend.
- Empty knowledge base: run 'python backend/scripts/seed_sample_data.py' after activating the backend environment.

## Security notes

- '.env', databases, Chroma data, uploads, logs, virtual environments, and Node build output are ignored by Git.
- API keys are read server-side from environment variables and are never required by the frontend.
- The default admin credentials are for local development only.
- Review authentication, authorization, audit, encryption, infrastructure, and contractual controls before production use.

## License

This project is licensed under the MIT License.

