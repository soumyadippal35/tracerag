from io import BytesIO
from pypdf import PdfReader
from .chunking import Chunk, chunk_text
from .retrieval import HybridRetriever


class DocumentStore:
    def __init__(self) -> None:
        self.retriever = HybridRetriever()
        self.documents: dict[str, dict] = {}

    def add_text(self, name: str, text: str, size: int = 0) -> dict:
        chunks = chunk_text(name, text)
        self.documents[name] = {"name": name, "chunks": len(chunks), "size": size}
        self._rebuild(chunks, name)
        return self.documents[name]

    def add_pdf(self, name: str, content: bytes) -> dict:
        reader = PdfReader(BytesIO(content))
        chunks: list[Chunk] = []
        for page_number, page in enumerate(reader.pages, 1):
            chunks.extend(chunk_text(name, page.extract_text() or "", page_number))
        self.documents[name] = {"name": name, "chunks": len(chunks), "size": len(content)}
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
