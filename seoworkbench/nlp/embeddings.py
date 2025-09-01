from __future__ import annotations

from typing import Iterable, List, Optional

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore

from ..config import get_settings


class EmbeddingModel:
    def __init__(self, model_name: Optional[str] = None) -> None:
        settings = get_settings()
        self.model_name = model_name or settings.HF_EMBEDDING_MODEL
        self._model = None
        if SentenceTransformer is not None:
            try:
                self._model = SentenceTransformer(self.model_name)
            except Exception:
                self._model = None

    def embed(self, texts: Iterable[str]) -> List[List[float]]:
        texts = [t if t is not None else "" for t in texts]
        if self._model is not None:
            vecs = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            return [v.tolist() for v in vecs]
        # Fallback: simple bag-of-words hashing (very rough)
        return [self._bow_hash(t) for t in texts]

    @staticmethod
    def _bow_hash(text: str, dim: int = 256) -> List[float]:
        arr = np.zeros(dim, dtype=np.float32)
        for tok in text.lower().split():
            idx = hash(tok) % dim
            arr[idx] += 1.0
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr /= norm
        return arr.tolist()

