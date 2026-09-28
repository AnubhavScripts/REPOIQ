<div align="center">

# 🧠 Repo IQ

**AI-powered repository intelligence — clone any GitHub repo, index it semantically, and chat with your codebase.**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![Qdrant](https://img.shields.io/badge/Vector%20DB-Qdrant-DC382D?style=for-the-badge)](https://qdrant.tech/)
[![Groq](https://img.shields.io/badge/LLM-Groq-F55036?style=for-the-badge)](https://groq.com/)
[![Gemini](https://img.shields.io/badge/Embeddings-Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Deploy-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

</div>

---

## 📖 Overview

**Repo IQ** is a full-stack AI application that lets you point it at any public GitHub repository URL and immediately start having a natural-language conversation with that codebase. Under the hood it:

1. **Clones** the repository to a temporary local workspace.
2. **Parses & chunks** every supported source file using language-aware text splitters.
3. **Embeds** all chunks with Google Gemini's `gemini-embedding-001` model and stores them in a **Qdrant** vector database.
4. **Answers questions** by retrieving the most semantically relevant code chunks and feeding them as context to **Groq's Llama 3.3 70B** model.

Everything is fully containerised with Docker, making it easy to run locally or deploy to any cloud provider.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔗 **One-click ingestion** | Paste a GitHub URL — the backend clones, parses, chunks and indexes in the background |
| 💬 **RAG-powered Q&A** | Ask architectural, implementation, or debugging questions in plain English |
| ⚡ **Async processing** | Ingestion runs as a FastAPI background task; the UI polls for status in real time |
| 🧩 **Multi-language parsing** | Python, JavaScript, TypeScript, JSX, TSX, Java, Go, C, C++ |
| 📦 **Containerised** | Single `docker compose up` command spins up the complete stack |
| 🗄️ **Persistent metadata** | PostgreSQL (via Neon) stores repositories and indexing job records |
| 🔍 **Semantic search** | Qdrant vector search returns the most relevant code chunks per question |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Browser (React)                        │
│  Home Page ──► paste URL ──► POST /api/ingest                  │
│  GET /api/status/{id} (polling)  ──► navigate to Chat Page     │
│  Chat Page ──► POST /api/chat ──► render answer                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP (Axios)
┌───────────────────────────▼─────────────────────────────────────┐
│                      FastAPI Backend                            │
│                                                                 │
│  /api/ingest  ──► BackgroundTask ──► Pipeline:                  │
│    1. clone_repository()   (GitPython)                         │
│    2. parse_repository()   (file walker + language detection)   │
│    3. chunk_repository_files() (LangChain text splitters)       │
│    4. generate_embeddings()    (Gemini Embedding API)           │
│    5. store_vectors()          (Qdrant)                         │
│                                                                 │
│  /api/status/{id} ──► PostgreSQL job status lookup             │
│                                                                 │
│  /api/chat ──► embed_query() ──► search_vectors()              │
│            ──► generate_response()  (Groq / Llama 3.3 70B)    │
└──────┬────────────────────────────────┬──────────────────────────┘
       │                                │
┌──────▼──────┐                ┌────────▼────────┐
│  PostgreSQL │                │     Qdrant      │
│  (Neon)     │                │  (Cloud / self) │
│  repos +    │                │  chunk vectors  │
│  jobs table │                └─────────────────┘
└─────────────┘
```

---

## 🗂️ Project Structure

```
Repo IQ/
├── backend/                        # FastAPI application
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py             # POST /api/chat
│   │   │   ├── ingest.py           # POST /api/ingest, GET /api/status
│   │   │   └── review.py           # (in progress)
│   │   ├── services/
│   │   │   ├── github_service.py   # Clone / delete repositories
│   │   │   ├── parser_service.py   # Walk repo, detect language, read files
│   │   │   ├── chunk_service.py    # Split files into chunks
│   │   │   ├── embedding_Service.py# Gemini embedding generation
│   │   │   └── llm_service.py      # Groq prompt building & inference
│   │   ├── vectorstore/
│   │   │   └── qdrant_Service.py   # Store & search vectors in Qdrant
│   │   ├── database/               # SQLAlchemy connection, models, CRUD
│   │   ├── models/                 # Pydantic request/response schemas
│   │   ├── config.py               # Pydantic settings (reads .env)
│   │   └── main.py                 # FastAPI app + routers
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example                # Environment variable template
│
├── frontend/                       # React + Vite SPA
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.jsx            # URL input + ingestion polling
│   │   │   └── Chat.jsx            # Chat interface
│   │   ├── services/
│   │   │   └── api.js              # Axios API client
│   │   └── App.jsx                 # React Router setup
│   ├── nginx.conf                  # Nginx config for production container
│   └── Dockerfile
│
└── docker-compose.yml              # Orchestrates backend + frontend
```

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- A [Qdrant](https://cloud.qdrant.io/) account (free tier works)
- A [Neon](https://neon.tech/) PostgreSQL database (free tier works)
- A [Google AI Studio](https://aistudio.google.com/) API key (for Gemini embeddings)
- A [Groq](https://console.groq.com/) API key (for LLM inference)

### 1 — Clone the repository

```bash
git clone https://github.com/AnubhavScripts/REPOIQ.git
cd REPOIQ
```

### 2 — Configure environment variables

Copy the example file and fill in your credentials:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
# PostgreSQL (Neon or any Postgres instance)
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

# Qdrant vector database
QDRANT_URL=https://<your-cluster>.qdrant.io
QDRANT_API_KEY=<your-qdrant-api-key>
QDRANT_COLLECTION=repo_iq_chunks

# Google Gemini (embeddings)
GEMINI_API_KEY=<your-gemini-api-key>
GEMINI_EMBEDDING_MODEL=models/gemini-embedding-001

# Groq (LLM inference)
GROQ_API_KEY=<your-groq-api-key>
GROQ_MODEL=llama-3.3-70b-versatile

# Application settings
TEMP_REPO_PATH=./temp_repos
ENVIRONMENT=development
DEBUG=True
MAX_REPO_SIZE_MB=50
MAX_FILES=1000
MAX_CHUNKS=3000
```

### 3 — Run with Docker Compose

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

### 4 — Run locally (without Docker)

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

---

## 🔌 API Reference

### `POST /api/ingest`
Submit a GitHub repository URL for indexing.

**Request body:**
```json
{ "repo_url": "https://github.com/owner/repo" }
```
**Response:**
```json
{ "repo_id": "42", "status": "PENDING" }
```

---

### `GET /api/status/{repo_id}`
Poll the indexing job status.

**Response:**
```json
{ "repo_id": "42", "status": "COMPLETED", "error_message": null }
```
Possible statuses: `PENDING` → `PROCESSING` → `COMPLETED` | `FAILED`

---

### `POST /api/chat`
Ask a question about an indexed repository.

**Request body:**
```json
{ "repo_id": "42", "question": "How is authentication handled?" }
```
**Response:**
```json
{ "answer": "Authentication is handled via JWT tokens in auth.py ..." }
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, React Router, Axios |
| **Backend** | FastAPI, SQLAlchemy, Pydantic v2 |
| **Database** | PostgreSQL (Neon serverless) |
| **Vector Store** | Qdrant Cloud |
| **Embeddings** | Google Gemini `gemini-embedding-001` |
| **LLM** | Groq — Llama 3.3 70B Versatile |
| **Code Splitting** | LangChain text splitters |
| **Git Cloning** | GitPython |
| **Containerisation** | Docker, Docker Compose, Nginx |

---

## 🗺️ Roadmap

- [ ] **Code Review endpoint** — automated AI code review per file or PR diff
- [ ] **Architecture diagram generation** — auto-generate mermaid diagrams from codebase
- [ ] **Private repository support** — GitHub OAuth / personal access token flow
- [ ] **Streaming responses** — server-sent events for real-time LLM output
- [ ] **Multi-repo workspaces** — compare or query across multiple indexed repos
- [ ] **File-level search** — browse indexed files and jump to relevant chunks

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push to the branch: `git push origin feat/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
Built with ❤️ by <a href="https://github.com/AnubhavScripts">Anubhav Parashar</a>
</div>
