from pydantic import BaseModel, Field


class Citation(BaseModel):
    document: str
    page: int | None = None
    snippet: str
    score: float


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=10)


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    retrieval_mode: str
    latency_ms: int


class DocumentSummary(BaseModel):
    name: str
    chunks: int
    size: int


class HealthResponse(BaseModel):
    status: str
    documents: int
    chunks: int


class AuthRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)


class AuthResponse(BaseModel):
    token: str
    email: str
