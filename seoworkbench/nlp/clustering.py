from __future__ import annotations

from typing import List, Tuple

import numpy as np

try:
    import hdbscan  # type: ignore
except Exception:  # pragma: no cover
    hdbscan = None  # type: ignore

from sklearn.cluster import AgglomerativeClustering


def cluster_embeddings(embeddings: List[List[float]], min_cluster_size: int = 5) -> List[int]:
    X = np.array(embeddings, dtype=np.float32)
    if hdbscan is not None and X.shape[0] >= min_cluster_size * 2:
        try:
            labels = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=2).fit_predict(X)
            return labels.tolist()
        except Exception:
            pass
    # Fallback: Agglomerative with heuristic cluster count
    n = X.shape[0]
    if n <= 1:
        return [0] * n
    k = max(2, min(10, n // max(2, min_cluster_size)))
    model = AgglomerativeClustering(n_clusters=k)
    labels = model.fit_predict(X)
    return labels.tolist()


def centroid(vectors: List[List[float]]) -> List[float]:
    X = np.array(vectors, dtype=np.float32)
    if X.size == 0:
        return []
    c = X.mean(axis=0)
    norm = np.linalg.norm(c)
    if norm > 0:
        c = c / norm
    return c.tolist()

