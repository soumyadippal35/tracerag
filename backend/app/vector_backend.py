"""Provider boundary for replacing local vectors with managed Qdrant or pgvector."""
import os


class ManagedVectorConfig:
    provider = os.getenv("TRAGERAG_VECTOR_PROVIDER", "local")
    url = os.getenv("TRAGERAG_VECTOR_URL")
    api_key = os.getenv("TRAGERAG_VECTOR_API_KEY")
    collection = os.getenv("TRAGERAG_VECTOR_COLLECTION", "tracerag_chunks")

    @classmethod
    def validate(cls) -> None:
        if cls.provider in {"qdrant", "pgvector"} and not cls.url:
            raise RuntimeError("TRAGERAG_VECTOR_URL is required for managed vector providers")
