from collections import Counter
import math
import re
from dataclasses import dataclass
import numpy as np
from .chunking import Chunk

TOKEN_RE = re.compile(r"[a-zA-Z0-9']+")


@dataclass
class ScoredChunk:
    chunk: Chunk
    score: float


class HybridRetriever:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []

    def replace(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks

    def _tokens(self, text: str) -> list[str]:
        return [token.lower() for token in TOKEN_RE.findall(text)]

    def _dense(self, text: str, dimensions: int = 192) -> np.ndarray:
        vector = np.zeros(dimensions)
        for token in self._tokens(text):
            vector[hash(token) % dimensions] += 1
        norm = np.linalg.norm(vector)
        return vector / norm if norm else vector

    def search(self, query: str, top_k: int = 5) -> list[ScoredChunk]:
        if not self.chunks:
            return []
        query_tokens = self._tokens(query)
        document_tokens = [self._tokens(chunk.text) for chunk in self.chunks]
        frequencies = Counter(token for tokens in document_tokens for token in set(tokens))
        avg_len = sum(map(len, document_tokens)) / max(len(document_tokens), 1)
        scores = []
        query_vector = self._dense(query)
        for chunk, tokens in zip(self.chunks, document_tokens):
            tf = Counter(tokens)
            lexical = 0.0
            for token in query_tokens:
                if token not in tf:
                    continue
                idf = math.log((len(self.chunks) - frequencies[token] + 0.5) / (frequencies[token] + 0.5) + 1)
                lexical += idf * (tf[token] * 2.2 / (tf[token] + 1.2 * (0.75 + 0.25 * len(tokens) / max(avg_len, 1))))
            dense = float(np.dot(query_vector, self._dense(chunk.text)))
            scores.append(ScoredChunk(chunk, 0.62 * lexical + 0.38 * dense))
        return sorted(scores, key=lambda item: item.score, reverse=True)[:top_k]
