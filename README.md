# TraceRAG

A production-shaped RAG workspace for asking grounded questions over internal documents. It combines BM25-style lexical retrieval with deterministic dense vectors, then returns an extractive answer with source snippets and match scores.

## Run locally

### 1. Start the API

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Start the web app

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and create an account. Upload `sample-docs/company-handbook.txt`, then ask: `What is our remote work policy?`

## What is included

- FastAPI upload and query API
- PDF, TXT, Markdown, and CSV ingestion
- Overlapping chunking with page-aware PDF citations
- Hybrid BM25 + deterministic dense retrieval
- Local extractive answer generation with no API key required
- React/Vite interface with evidence expansion, latency, and indexing state
- Focused API test
- Signed authentication with protected routes
- Three.js knowledge-space visualization
- Nginx same-origin API proxy for container deployment

## Docker

```powershell
docker compose up --build
```

The frontend is available at http://localhost:5173 and the API at http://localhost:8000.

## Production next steps

Before public release, set a strong `TRAGERAG_AUTH_SECRET`, add HTTPS and rate limiting, use a managed identity provider, and move retrieval to Qdrant or pgvector. The current local extractive answerer is intentionally keyless and interview-friendly; it is not a substitute for an evaluated LLM answer service.
