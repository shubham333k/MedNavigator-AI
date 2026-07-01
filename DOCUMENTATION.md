# Healthcare Knowledge Navigator for Clinicians
**Comprehensive Documentation**

## 1. Project Overview
The **Healthcare Knowledge Navigator** is an AI-powered clinical decision support system designed specifically for healthcare professionals. It provides evidence-based answers to medical queries and assists in differential diagnosis through an interactive AI assistant. The system leverages Retrieval-Augmented Generation (RAG) to ground its responses in verified medical literature (e.g., PubMed, uploaded clinical guidelines) and uses a robust Role-Based Access Control (RBAC) model to ensure security and compliance.

---

## 2. Architecture & Tech Stack

The application is built on a modern, decoupled architecture:

### 2.1. Frontend
- **Framework**: Next.js 14 (App Router) with React 18
- **Language**: TypeScript
- **Styling**: Vanilla CSS with modern, dark-themed glassmorphism aesthetics
- **Key Components**:
  - `DiagnosticChat`: Interactive UI for differential diagnosis.
  - `Navbar` & `Sidebar`: Navigation and Role-based Badges.
  - `api.ts`: Centralized fetch client for backend communication.

### 2.2. Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite (managed via SQLAlchemy ORM)
- **Vector Database**: ChromaDB (for local embedding storage and semantic search)
- **LLM Integration**: LangChain and LangGraph for orchestrating LLM workflows
- **Authentication**: JWT-based authentication with `python-jose`

### 2.3. AI / Machine Learning
- **Embedding Model**: `BAAI/bge-large-en-v1.5` (HuggingFace) for high-quality semantic representations of medical text.
- **LLM Provider**: Configured primarily for Google Gemini (e.g., `gemini-2.5-flash`), with fallback support for Anthropic Claude or OpenAI for strict HIPAA-compliant environments.

---

## 3. Core Features

### 3.1. Diagnostic Assistant
An interactive conversational agent that guides clinicians through differential diagnosis.
- **Workflow**: The clinician inputs symptoms, age, sex, and medical history. The agent uses LangGraph to gather context from the vector database, reason over the symptoms, and formulate a list of potential conditions with confidence scores. It may ask follow-up questions to refine the diagnosis.
- **Safety**: A prominent warning emphasizes that the tool is for clinical decision support only and does not replace physician judgment.

### 3.2. Medical Querying (RAG)
Allows users to ask open-ended medical questions.
- The system retrieves the most relevant document chunks from ChromaDB and synthesizes an answer using the LLM.
- **Citations**: Responses include direct citations and references to the source material to ensure transparency and trust.

### 3.3. Role-Based Access Control (RBAC)
Three distinct roles are enforced across the platform:
- **Admin**: Full access to all features, user management, and system logs.
- **Clinician**: Can execute general queries and use the Diagnostic Assistant.
- **Viewer**: Read-only access to knowledge base and past queries; cannot start new diagnostic sessions.

---

## 4. Setup and Installation

### 4.1. Prerequisites
- Node.js (v18+)
- Python (3.11+)
- Google Gemini API Key (or OpenAI / Anthropic Key)

### 4.2. Backend Setup
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables by copying `.env.example` to `.env` in the root and in the backend folder, ensuring you set the `GOOGLE_API_KEY`.
5. Start the backend server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 4.3. Frontend Setup
1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Access the application at `http://localhost:3000`.

---

## 5. Security & Privacy Considerations
- **No PHI Storage**: The application is designed to process symptoms in-memory. Clinicians are warned not to enter Protected Health Information (PHI) such as names, MRNs, or dates of birth.
- **Encryption**: Sensitive database fields (where applicable) are encrypted using Fernet symmetric encryption.
- **Local Vectors**: ChromaDB runs locally, ensuring that medical guidelines and ingested documents never leave your server's perimeter.

---

## 6. API Reference (Key Endpoints)

- `POST /api/auth/login`: Authenticate and receive JWT token.
- `POST /api/query/`: Submit a general medical query (RAG).
- `POST /api/diagnostic/start`: Initiate a new diagnostic session with initial symptoms.
- `POST /api/diagnostic/respond`: Respond to the agent's follow-up questions.
- `GET /health`: System health and configuration check.
