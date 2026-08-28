import re
from .retrieval import ScoredChunk


def build_answer(question: str, results: list[ScoredChunk]) -> str:
    if not results or results[0].score <= 0:
        return "I couldn't find enough support in the indexed documents to answer that confidently. Try adding a relevant document or rephrasing the question."
    question_terms = set(re.findall(r"[a-zA-Z0-9']+", question.lower()))
    sentences: list[tuple[float, str]] = []
    for result in results:
        for sentence in re.split(r"(?<=[.!?])\s+", result.chunk.text):
            terms = set(re.findall(r"[a-zA-Z0-9']+", sentence.lower()))
            overlap = len(question_terms & terms)
            if sentence.strip():
                sentences.append((result.score + overlap * 0.04, sentence.strip()))
    selected = []
    seen = set()
    for _, sentence in sorted(sentences, reverse=True):
        key = sentence.lower()
        if key not in seen:
            selected.append(sentence)
            seen.add(key)
        if len(selected) == 3:
            break
    return " ".join(selected) if selected else results[0].chunk.text
