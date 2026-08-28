from dataclasses import dataclass
import re


@dataclass
class Chunk:
    document: str
    text: str
    page: int | None
    index: int


def chunk_text(document: str, text: str, page: int | None = None, size: int = 850, overlap: int = 120) -> list[Chunk]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    chunks = []
    start = 0
    index = 0
    while start < len(cleaned):
        end = min(start + size, len(cleaned))
        if end < len(cleaned):
            boundary = cleaned.rfind(" ", start, end)
            end = boundary if boundary > start + size // 2 else end
        chunks.append(Chunk(document, cleaned[start:end].strip(), page, index))
        index += 1
        if end >= len(cleaned):
            break
        start = max(end - overlap, start + 1)
    return chunks
