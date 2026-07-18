import math
from typing import List, Dict, Any, Tuple

class LocalVectorDB:
    """In-memory cosine vector store with Pinecone/Qdrant-compatible schema."""

    def __init__(self):
        self.vectors: List[Dict[str, Any]] = []

    def _simple_embed(self, text: str) -> List[float]:
        # Deterministic 16-dim pseudo-embedding for local offline testing
        words = text.lower().split()
        vec = [0.0] * 16
        for i, w in enumerate(words):
            val = sum(ord(c) for c in w) % 100 / 100.0
            vec[i % 16] += val
        norm = math.sqrt(sum(x*x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def upsert(self, doc_id: str, text: str, metadata: Dict[str, Any]):
        vec = self._simple_embed(text)
        self.vectors.append({
            "id": doc_id,
            "vector": vec,
            "text": text,
            "metadata": metadata
        })

    def query(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        q_vec = self._simple_embed(query_text)
        scored = []
        for doc in self.vectors:
            sim = sum(a * b for a, b in zip(q_vec, doc["vector"]))
            scored.append((sim, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"score": round(s, 4), "doc": d} for s, d in scored[:top_k]]
