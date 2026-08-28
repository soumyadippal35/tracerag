import os
from pathlib import Path
from time import perf_counter
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .answering import build_answer
from .models import DocumentSummary, HealthResponse, QueryRequest, QueryResponse, Citation
from .store import DocumentStore

app = FastAPI(title="TraceRAG API", version="1.0.0")
allowed_origins = [origin.strip() for origin in os.getenv("TRAGERAG_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_methods=["*"], allow_headers=["*"])
store = DocumentStore()


@app.get("/api/health", response_model=HealthResponse)
def health():
    documents, chunks = store.stats()
    return {"status": "operational", "documents": documents, "chunks": chunks}


@app.get("/api/documents", response_model=list[DocumentSummary])
def documents():
    return store.list_documents()


@app.post("/api/documents/upload", response_model=DocumentSummary)
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(413, "Files must be smaller than 10 MB")
    if not file.filename:
        raise HTTPException(400, "A file name is required")
    suffix = Path(file.filename).suffix.lower()
    if suffix == ".pdf":
        summary = store.add_pdf(file.filename, content)
    elif suffix in {".txt", ".md", ".csv"}:
        summary = store.add_text(file.filename, content.decode("utf-8", errors="ignore"), len(content))
    else:
        raise HTTPException(415, "Supported files: PDF, TXT, MD, CSV")
    return summary


@app.post("/api/query", response_model=QueryResponse)
def query(request: QueryRequest):
    started = perf_counter()
    results = store.search(request.question, request.top_k)
    citations = [Citation(document=item.chunk.document, page=item.chunk.page, snippet=item.chunk.text[:240], score=round(item.score, 3)) for item in results if item.score > 0]
    return QueryResponse(answer=build_answer(request.question, results), citations=citations, retrieval_mode="hybrid - BM25 + dense", latency_ms=round((perf_counter() - started) * 1000))
