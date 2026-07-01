<div align="center">

# 🏥 MedNavigator-AI

### *AI-Powered Clinical Knowledge Navigation System*

<p>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js"/>
  <img src="https://img.shields.io/badge/Google_Gemini-FF6D00?style=for-the-badge&logo=google&logoColor=white" alt="Gemini"/>
  <img src="https://img.shields.io/badge/ChromaDB-FF4B4B?style=for-the-badge&logo=databricks&logoColor=white" alt="ChromaDB"/>
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white" alt="LangChain"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/>
</p>

<p>
  <strong>A HIPAA-compliant Retrieval-Augmented Generation (RAG) platform that empowers clinicians to query medical literature, clinical guidelines, and drug databases using natural language.</strong>
</p>

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start (Docker)](#-quick-start-docker)
- [Local Development](#-local-development)
- [API Reference](#-api-reference)
- [Security & HIPAA Compliance](#-security--hipaa-compliance)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**MedNavigator-AI** is a production-grade, AI-powered assistant built specifically for the healthcare domain. It solves the core problem clinicians face daily — the overwhelming volume of medical literature and the difficulty of extracting relevant, evidence-based answers quickly and safely.

By combining **Google Gemini 2.5** as the language engine with a **Retrieval-Augmented Generation (RAG)** pipeline, MedNavigator-AI retrieves the most relevant chunks from your private medical knowledge base before generating a response. This approach:

- ✅ **Reduces hallucinations** by grounding answers in real source documents
- ✅ **Provides citations** for every answer so clinicians can verify the source
- ✅ **Keeps data private** — your knowledge base stays on your infrastructure
- ✅ **Maintains HIPAA compliance** through PHI de-identification and audit logging

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔍 **Natural Language Queries** | Ask complex medical questions in plain English and get precise, evidence-backed answers |
| 🧠 **Diagnostic Assistant** | LangGraph-powered agentic workflow for differential diagnosis from patient symptoms |
| 📚 **Multi-Source Ingestion** | Ingest PubMed abstracts, clinical PDF guidelines, drug CSV databases, and plain text |
| 📊 **Citation Tracking** | Every AI response includes exact references to the source documents used |
| 🔒 **HIPAA Compliance** | JWT auth, Role-Based Access Control (RBAC), PHI de-identification, and audit logs |
| 🔐 **Data Encryption** | Field-level encryption for sensitive data using Fernet symmetric keys |
| 👤 **Role Management** | Admin, Clinician, and Viewer roles with granular permission control |
| 🐳 **Docker Ready** | Full Docker Compose setup for zero-friction deployment |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Clinician Browser                          │
│                  Next.js 14 (React + TypeScript)                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │  HTTPS / REST API
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│   ┌──────────┐  ┌──────────────┐  ┌───────────────────────┐    │
│   │  Auth &  │  │  RAG Query   │  │  LangGraph Diagnostic  │    │
│   │  RBAC    │  │  Pipeline    │  │  Agent Workflow        │    │
│   └──────────┘  └──────┬───────┘  └───────────┬───────────┘    │
└────────────────────────│──────────────────────│────────────────┘
                         │                      │
           ┌─────────────▼──────────────────────▼──────────┐
           │              LangChain Orchestration           │
           │  ┌─────────────────┐    ┌──────────────────┐  │
           │  │  ChromaDB       │    │  Google Gemini   │  │
           │  │  (Vector Store) │◄───│  2.5 Flash (LLM) │  │
           │  └─────────────────┘    └──────────────────┘  │
           └────────────────────────────────────────────────┘
                         ▲
           ┌─────────────┴───────────────┐
           │      Ingestion Pipeline     │
           │  PDFs │ PubMed │ CSV │ Text │
           └─────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Next.js 14, React, TypeScript | Clinician-facing UI |
| **Backend** | FastAPI, Python 3.11+ | REST API server |
| **AI Orchestration** | LangChain, LangGraph | RAG pipeline & agent workflows |
| **Language Model** | Google Gemini 2.5 Flash | Response generation |
| **Embeddings** | `BAAI/bge-large-en-v1.5` | Semantic document search |
| **Vector Database** | ChromaDB | Storing & retrieving document embeddings |
| **Relational DB** | SQLite (dev) / PostgreSQL (prod) | User accounts, audit logs |
| **Authentication** | JWT + Refresh Tokens | Secure session management |
| **Authorization** | RBAC Middleware | Role-based access control |
| **Containerization** | Docker, Docker Compose | Deployment & orchestration |
| **CI/CD** | GitHub Actions | Automated testing & linting |

---

## 📂 Project Structure

```
MedNavigator-AI/
│
├── 📁 frontend/                    # Next.js React Application
│   ├── src/
│   │   ├── app/                    # Next.js App Router pages
│   │   │   ├── login/              # Authentication page
│   │   │   ├── query/              # Medical Q&A interface
│   │   │   ├── ingest/             # Document ingestion UI
│   │   │   └── diagnostic/         # Diagnostic assistant chat
│   │   ├── components/             # Reusable UI components
│   │   └── lib/                    # API client & auth helpers
│   ├── Dockerfile
│   └── package.json
│
├── 📁 backend/                     # FastAPI Python Server
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/             # Endpoint handlers
│   │   │   │   ├── auth.py         # Login, logout, refresh
│   │   │   │   ├── query.py        # RAG query endpoint
│   │   │   │   ├── ingest.py       # Document upload endpoint
│   │   │   │   └── diagnostic.py   # Agentic diagnostic endpoint
│   │   │   └── middleware/
│   │   │       ├── auth.py         # JWT verification middleware
│   │   │       └── audit.py        # HIPAA audit logging
│   │   ├── core/
│   │   │   ├── llm.py              # Gemini LLM setup
│   │   │   ├── embeddings.py       # BGE embeddings manager
│   │   │   ├── vectorstore.py      # ChromaDB connection
│   │   │   └── prompts.py          # System prompt templates
│   │   ├── rag/
│   │   │   ├── chain.py            # Full RAG chain definition
│   │   │   ├── retriever.py        # Document retriever logic
│   │   │   └── citations.py        # Source citation formatter
│   │   ├── agents/
│   │   │   ├── diagnostic.py       # LangGraph agent definition
│   │   │   └── state.py            # Agent state schema
│   │   ├── ingestion/
│   │   │   ├── pipeline.py         # Orchestration pipeline
│   │   │   ├── parsers.py          # PDF, CSV, text parsers
│   │   │   ├── chunker.py          # Document chunking strategy
│   │   │   └── pubmed.py           # PubMed API integration
│   │   ├── security/
│   │   │   ├── rbac.py             # Role-based access control
│   │   │   ├── deidentify.py       # PHI scrubber
│   │   │   └── encryption.py       # Fernet encryption
│   │   ├── models/
│   │   │   ├── schemas.py          # Pydantic request/response models
│   │   │   └── database.py         # SQLAlchemy ORM models
│   │   ├── config.py               # Centralized settings (env vars)
│   │   └── main.py                 # FastAPI app entry point
│   ├── tests/                      # Pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
│
├── 📄 docker-compose.yml           # Multi-service orchestration
├── 📄 .env.example                 # Environment variable template
├── 📄 .gitignore
└── 📁 .github/workflows/           # CI/CD pipeline definitions
```

---

## 🚀 Quick Start (Docker)

The fastest way to run the full stack locally.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- A free [Google Gemini API Key](https://aistudio.google.com/app/apikey)

### Step 1 — Clone the repository

```bash
git clone https://github.com/shubham333k/MedNavigator-AI.git
cd MedNavigator-AI
```

### Step 2 — Configure environment

```bash
cp .env.example .env
```

Open `.env` and set your API key:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
JWT_SECRET_KEY=your_long_random_secret_key_here
```

### Step 3 — Launch with Docker Compose

```bash
docker-compose up --build
```

### Step 4 — Access the application

| Service | URL |
|---|---|
| 🌐 Frontend UI | http://localhost:3000 |
| ⚙️ Backend API | http://localhost:8000 |
| 📖 API Swagger Docs | http://localhost:8000/docs |

**Default credentials:**

```
Email:    admin@healthcare.nav
Password: admin123
```

> ⚠️ **Change the default password immediately for any non-local environment.**

---

## 💻 Local Development

Run each service individually for a faster development feedback loop.

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Start the dev server with hot-reload
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend will be available at **http://localhost:3000**. It connects to the backend automatically via the `NEXT_PUBLIC_API_URL` environment variable.

---

## 📡 API Reference

Key endpoints exposed by the FastAPI backend:

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/login` | Authenticate and receive JWT tokens | No |
| `POST` | `/api/auth/refresh` | Refresh an expired access token | No |
| `POST` | `/api/query/` | Run a RAG query against the knowledge base | Yes |
| `POST` | `/api/ingest/upload` | Upload a PDF, CSV, or text file for ingestion | Yes (Admin) |
| `POST` | `/api/ingest/pubmed` | Fetch and ingest PubMed abstracts by keyword | Yes (Admin) |
| `POST` | `/api/diagnostic/` | Start an agentic diagnostic workflow | Yes |
| `GET` | `/health` | System health check | No |
| `GET` | `/docs` | Interactive Swagger UI | No |

---

## Highlights

- Built healthcare-focused RAG platform using LangGraph and ChromaDB
- Implemented semantic search over medical knowledge sources
- Integrated Gemini LLM for context-aware responses
- Developed full-stack application using FastAPI and Next.js
- Containerized deployment using Docker

## 🔒 Security & HIPAA Compliance

MedNavigator-AI is built with enterprise healthcare security requirements in mind:

- **🔑 JWT Authentication** — Stateless, short-lived access tokens with refresh token rotation
- **👮 Role-Based Access Control (RBAC)** — Three roles: `Admin`, `Clinician`, `Viewer` with enforced permission boundaries
- **🧹 PHI De-identification** — Automatic scrubbing of Protected Health Information before any data is logged or indexed
- **📝 Audit Logging** — Every query, login event, and data access is timestamped and recorded in a tamper-evident audit log
- **🔐 Field-Level Encryption** — Sensitive database fields encrypted using Fernet symmetric encryption
- **🛡️ CORS Protection** — Strict origin validation on all API endpoints
- **🔒 Secrets Management** — All credentials loaded from environment variables; never hardcoded

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Please ensure your code passes the existing test suite:

```bash
cd backend
pytest tests/ -v
```

---

## 📄 License

This project is licensed under the **MIT License**.

> **Disclaimer:** MedNavigator-AI is built for educational and demonstration purposes. It is **not** a certified medical device and should **not** be used as a substitute for professional medical advice, diagnosis, or treatment.

---

<div align="center">

Built with ❤️ by [Shubham](https://github.com/shubham333k)

⭐ If you found this project useful, please give it a star!

</div>
