<div align="center">

# 🏥 MedNavigator-AI

### <i>AI-Powered Clinical Knowledge Navigation System</i>

<p>
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.165-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js"/>
  <img src="https://img.shields.io/badge/Google_Gemini-3.5_Flash_Lite-FF6D00?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini"/>
  <img src="https://img.shields.io/badge/ChromaDB-Vector_Store-FF4B4B?style=for-the-badge" alt="ChromaDB"/>
  <img src="https://img.shields.io/badge/LangChain-1.5-1C3C3C?style=for-the-badge" alt="LangChain"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License"/>
</p>

<strong>A Retrieval-Augmented Generation (RAG) platform that helps clinicians query medical literature, clinical guidelines, and drug references using natural language.</strong>

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start with Docker](#-quick-start-with-docker)
- [Local Development](#-local-development)
- [API Reference](#-api-reference)
- [Screenshots](#-screenshots)
- [Security and HIPAA-aligned Controls](#-security-and-hipaa-aligned-controls)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

MedNavigator-AI is a full-stack clinical knowledge navigation system built around retrieval-augmented generation. The application retrieves relevant chunks from an indexed medical knowledge base and includes source citations with generated responses.

The platform demonstrates authentication, role-based access control, document ingestion, semantic retrieval, citations, and an agentic diagnostic workflow in a healthcare-focused application.

> **Important:** This project provides HIPAA-aligned security controls for educational purposes. It is not HIPAA-certified, a medical device, or a substitute for professional medical advice.

### Default local account

~~~~text
Email:    admin@healthcare.nav
Password: admin123
~~~~

Change the password before using the application outside local development.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔍 **Natural Language Queries** | Ask medical questions in plain language and receive evidence-grounded responses. |
| 🧠 **RAG Pipeline** | Retrieve relevant document chunks from ChromaDB before generating an answer. |
| 📚 **Multi-Source Ingestion** | Ingest PDF, text, CSV, JSON, sample data, and PubMed abstracts. |
| 🧾 **Citation Tracking** | Return source titles, snippets, relevance scores, and links with answers. |
| 🩺 **Diagnostic Assistant** | Use a LangGraph workflow for symptom-based differential diagnosis. |
| 🔐 **Authentication** | Use JWT access tokens, refresh tokens, and protected API routes. |
| 👥 **RBAC** | Support Admin, Clinician, and Viewer roles with permission boundaries. |
| 🛡️ **Security Controls** | Include PHI de-identification, audit logging, and Fernet encryption support. |
| 🐳 **Docker Ready** | Run the frontend, backend, and ChromaDB with Docker Compose. |
| 🧪 **Tested Workflow** | Include backend tests, frontend type checking, and production build validation. |

---

## 🏗️ Architecture

~~~~text
┌──────────────────────────────────────────────────────────────┐
│                        Clinician Browser                     │
│                Next.js 14 + React + TypeScript               │
└───────────────────────────────┬──────────────────────────────┘
                                │ REST API + JWT
                                ▼
┌──────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                        │
│  Auth/RBAC │ Query API │ Ingestion API │ Diagnostic API       │
└───────────────┬───────────────────────┬──────────────────────┘
                │                       │
                ▼                       ▼
┌────────────────────────┐   ┌─────────────────────────────────┐
│ SQLite                 │   │ RAG and Agent Layer             │
│ Users, history, audit  │   │ LangChain + LangGraph            │
└────────────────────────┘   └───────────────┬─────────────────┘
                                             │
                         ┌───────────────────┴──────────────────┐
                         ▼                                      ▼
                ┌─────────────────┐                    ┌──────────────────┐
                │ ChromaDB        │                    │ Google Gemini    │
                │ Vector retrieval│                    │ 3.5 Flash Lite   │
                └────────┬────────┘                    └──────────────────┘
                         ▲
                         │
                ┌────────┴────────┐
                │ BGE Embeddings  │
                │ CPU/GPU aware   │
                └─────────────────┘
~~~~

### Request flow

1. The user authenticates through the Next.js login page.
2. The frontend attaches the JWT access token to protected API calls.
3. The backend validates the token and role permissions.
4. The query is embedded and matched against ChromaDB.
5. Retrieved documents are injected into the RAG prompt.
6. Gemini generates a grounded answer.
7. Citations are extracted and returned to the frontend.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Next.js 14, React 18, TypeScript | Clinician-facing dashboard and workflows |
| Backend | FastAPI, Python 3.12 | REST API and application services |
| LLM | Google Gemini 3.5 Flash Lite | Response generation |
| AI orchestration | LangChain 1.5, LangGraph 1.2 | RAG and diagnostic workflows |
| Embeddings | BAAI/bge-small-en-v1.5 | Local semantic embeddings |
| Vector database | ChromaDB 1.5 | Persistent similarity search |
| Relational database | SQLite, SQLAlchemy | Users, audit, history, and ingestion metadata |
| Authentication | JWT, python-jose | Access and refresh tokens |
| Security | bcrypt, cryptography | Password hashing and encryption utilities |
| Document parsing | PyPDF2, python-docx, CSV/JSON parsers | Document extraction |
| Containerization | Docker, Docker Compose | Local multi-service deployment |
| CI/CD | GitHub Actions | Automated tests and frontend checks |

---

## 📁 Project Structure

~~~~text
MedNavigator-AI/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI routes and middleware
│   │   ├── agents/          # LangGraph diagnostic workflow
│   │   ├── core/            # Settings, LLM, embeddings, ChromaDB
│   │   ├── ingestion/       # Parsers, chunking, PubMed, pipeline
│   │   ├── models/          # SQLAlchemy and Pydantic models
│   │   ├── rag/             # Retrieval, generation, citations
│   │   └── security/        # RBAC, encryption, de-identification
│   ├── scripts/             # Seed and maintenance scripts
│   ├── sample_data/         # Small text and PDF fixtures
│   ├── tests/               # Pytest suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/app/             # Next.js pages
│   ├── src/components/      # Reusable UI components
│   ├── src/lib/             # API client and auth helpers
│   └── package.json
├── .github/workflows/       # CI/CD workflow
├── docker-compose.yml
├── render.yaml
├── .env.example
└── README.md
~~~~

---

## 🚀 Quick Start with Docker

### Prerequisites

- Docker Desktop installed and running
- A valid Google Gemini API key
- Git

### 1. Clone and configure

~~~~powershell
git clone https://github.com/shubham333k/MedNavigator-AI.git
cd MedNavigator-AI
Copy-Item .env.example .env
~~~~

Edit .env:

~~~~env
GOOGLE_API_KEY=your_google_ai_studio_key
JWT_SECRET_KEY=replace-with-a-long-random-secret
GEMINI_MODEL=gemini-3.5-flash-lite
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
~~~~

### 2. Start the stack

~~~~powershell
docker compose up --build
~~~~

### 3. Open the services

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:8000 |
| Swagger API docs | http://localhost:8000/docs |
| ChromaDB | http://localhost:8100 |

---

## 💻 Local Development

### Backend

~~~~powershell
cd backend
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt
~~~~

Create backend/.env from the root template and set:

~~~~env
GOOGLE_API_KEY=your_google_ai_studio_key
JWT_SECRET_KEY=replace-with-a-long-random-secret
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
GEMINI_MODEL=gemini-3.5-flash-lite
CHROMA_DATA_PATH=./chroma_data
~~~~

Start the API:

~~~~powershell
uvicorn app.main:app --reload --port 8000
~~~~

### Seed sample documents

Stop the backend before running a separate seed process.

~~~~powershell
python scripts/seed_sample_data.py
~~~~

The first run downloads the embedding model and caches it locally.

### Frontend

In frontend/.env.local:

~~~~env
NEXT_PUBLIC_API_URL=http://localhost:8000
~~~~

Start the frontend in another terminal:

~~~~powershell
cd frontend
npm install
npm run dev
~~~~

Open http://localhost:3000 and sign in with the local admin account.

> Do not run npm run build at the same time as npm run dev; both use the .next directory.

---

## 📡 API Reference

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| GET | /health | Service health check | None |
| POST | /api/auth/login | Login and receive JWT tokens | None |
| POST | /api/auth/refresh | Refresh an access token | Refresh token |
| POST | /api/query/ | Run a cited RAG query | JWT |
| POST | /api/ingest/upload | Upload and ingest a document | Admin |
| POST | /api/ingest/pubmed | Fetch and ingest PubMed abstracts | Admin |
| POST | /api/ingest/sample-data | Load built-in sample documents | Admin |
| POST | /api/diagnostic/start | Start a diagnostic workflow | JWT |
| POST | /api/diagnostic/respond | Continue a diagnostic workflow | JWT |
| GET | /docs | Open Swagger UI | None |

---

## 📸 Screenshots

Dashboard screenshots can be added under docs/screenshots/. The table below gives the recommended names and order for project screenshots.

| Screenshot | File to add | What it should show |
|---|---|---|
| 🏠 Dashboard | docs/screenshots/dashboard.png | Main dashboard and navigation |
| 🔍 Medical Query | docs/screenshots/query.png | Query input, generated answer, and citations |
| 📚 Knowledge Base | docs/screenshots/knowledge-base.png | Sample data, upload, or PubMed ingestion |
| 🩺 Diagnostic Assistant | docs/screenshots/diagnostic.png | Symptom input and diagnostic workflow |
| 🔐 Login | docs/screenshots/login.png | Authentication screen |

> Add the image files with these exact names and they can be embedded directly in this section. See docs/screenshots/README.md for the screenshot checklist.

---

## 🔒 Security and HIPAA-aligned Controls

This project is educational and is not HIPAA-certified.

- JWT authentication with access and refresh tokens
- Role-based access control for Admin, Clinician, and Viewer users
- Password hashing with bcrypt
- PHI de-identification utilities
- Audit logging middleware
- Fernet encryption utilities for sensitive fields
- CORS configuration for local frontend origins
- Environment-based secret management
- No API keys or local databases committed to Git

Production deployments still require a formal security review, infrastructure controls, agreements, monitoring, backups, and operational procedures.

---

## 🧪 Testing

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

The repository CI workflow installs dependencies and runs backend and frontend checks automatically.

---

## 🧯 Troubleshooting

| Problem | Solution |
|---|---|
| Authentication required | Sign in first. The frontend redirects to /login when the access token is missing or expired. |
| Gemini NOT_FOUND | Set GEMINI_MODEL=gemini-3.5-flash-lite and restart Uvicorn. |
| Gemini 503 UNAVAILABLE | Retry after a short wait or choose another available Flash model. |
| Chroma HNSW disk error | Stop the backend, remove backend/chroma_data, seed again, and restart the backend. |
| Empty knowledge base | Run python scripts/seed_sample_data.py from backend/. |
| Slow first ingestion | Expected: the BGE model is downloaded once and cached locally. |

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make your changes and add tests where appropriate.
4. Run the backend tests and frontend checks.
5. Open a pull request with a clear description.

---

## 📄 License

This project is licensed under the MIT License.

<div align="center">

Built for educational demonstration of clinical RAG workflows.

⭐ If this project was useful, consider starring the repository.

</div>

