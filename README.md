# 🏥 Healthcare Knowledge Navigator

A **HIPAA-compliant Retrieval-Augmented Generation (RAG)** system designed to assist clinicians in navigating medical literature, clinical guidelines, and drug databases using natural language.

## Features

- 🔍 **Natural Language Medical Queries** — Ask complex medical questions and get evidence-based responses with citations
- 🧠 **Diagnostic Assistant** — LangGraph-powered agent for differential diagnosis based on patient symptoms
- 📚 **Medical Knowledge Base** — Ingest PubMed abstracts, clinical guidelines (PDF), and drug databases
- 🔒 **HIPAA Compliance** — JWT auth, RBAC, PHI de-identification, audit logging, data encryption
- 📊 **Citation Tracking** — Every response cites its source documents

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (React + TypeScript) |
| Backend API | FastAPI (Python 3.11+) |
| Orchestration | LangChain + LangGraph |
| LLM | Google Gemini 2.5 Flash |
| Embeddings | BAAI/bge-large-en-v1.5 (local) |
| Vector DB | ChromaDB |
| Auth | JWT + RBAC |
| Deployment | Docker Compose |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Gemini API Key

### 1. Clone and configure
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run with Docker Compose
```bash
docker-compose up --build
```

### 3. Access the application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Default Login
```
Email: admin@healthcare.nav
Password: admin123
```

## Local Development

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure
```
Healthcare/
├── frontend/          # Next.js application
├── backend/           # FastAPI + LangChain/LangGraph
│   ├── app/
│   │   ├── api/       # API routes & middleware
│   │   ├── core/      # AI pipeline (embeddings, LLM, vectorstore)
│   │   ├── rag/       # RAG chain & retriever
│   │   ├── agents/    # LangGraph diagnostic assistant
│   │   ├── ingestion/ # Data ingestion pipeline
│   │   ├── security/  # Auth, encryption, RBAC
│   │   └── models/    # Pydantic schemas & database
│   └── data/          # Sample medical data
├── docker-compose.yml
└── .github/workflows/ # CI/CD
```

## License

This project is for educational and demonstration purposes.
