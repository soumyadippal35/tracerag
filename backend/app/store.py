from io import BytesIO
import os
import sqlite3
from pathlib import Path
from pypdf import PdfReader
from .chunking import Chunk, chunk_text
from .retrieval import HybridRetriever


class DocumentStore:
    def __init__(self) -> None:
        self.retriever = HybridRetriever()
        self.db_path = Path(os.getenv("TRAGERAG_DB_PATH", "data/tracerag.db"))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.documents: dict[str, dict] = {}
        self._init_db()
        self._load()

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS documents (
                    name TEXT PRIMARY KEY, chunks INTEGER NOT NULL, size INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, document TEXT NOT NULL,
                    text TEXT NOT NULL, page INTEGER, chunk_index INTEGER NOT NULL,
                    FOREIGN KEY(document) REFERENCES documents(name) ON DELETE CASCADE
                );
            """)

    def _load(self) -> None:
        with self._connect() as connection:
            self.documents = {row["name"]: dict(row) for row in connection.execute("SELECT name, chunks, size FROM documents")}
            rows = connection.execute("SELECT document, text, page, chunk_index FROM chunks ORDER BY id")
        self.retriever.replace([Chunk(row["document"], row["text"], row["page"], row["chunk_index"]) for row in rows])

    def _save(self, name: str, summary: dict, chunks: list[Chunk]) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("DELETE FROM chunks WHERE document = ?", (name,))
            connection.execute("INSERT OR REPLACE INTO documents(name, chunks, size) VALUES (?, ?, ?)", (name, summary["chunks"], summary["size"]))
            connection.executemany("INSERT INTO chunks(document, text, page, chunk_index) VALUES (?, ?, ?, ?)", [(chunk.document, chunk.text, chunk.page, chunk.index) for chunk in chunks])

    def add_text(self, name: str, text: str, size: int = 0) -> dict:
        chunks = chunk_text(name, text)
        summary = {"name": name, "chunks": len(chunks), "size": size}
        self.documents[name] = summary
        self._save(name, summary, chunks)
        self._rebuild(chunks, name)
        return self.documents[name]

    def add_pdf(self, name: str, content: bytes) -> dict:
        reader = PdfReader(BytesIO(content))
        chunks: list[Chunk] = []
        for page_number, page in enumerate(reader.pages, 1):
            chunks.extend(chunk_text(name, page.extract_text() or "", page_number))
        summary = {"name": name, "chunks": len(chunks), "size": len(content)}
        self.documents[name] = summary
        self._save(name, summary, chunks)
        self._rebuild(chunks, name)
        return self.documents[name]

    def _rebuild(self, new_chunks: list[Chunk], name: str) -> None:
        existing = [chunk for chunk in self.retriever.chunks if chunk.document != name]
        self.retriever.replace(existing + new_chunks)

    def search(self, question: str, top_k: int):
        return self.retriever.search(question, top_k)

    def stats(self) -> tuple[int, int]:
        return len(self.documents), len(self.retriever.chunks)

    def list_documents(self) -> list[dict]:
        return list(self.documents.values())
