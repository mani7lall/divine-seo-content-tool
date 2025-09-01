from __future__ import annotations

from typing import Iterable, List

from sklearn.feature_extraction.text import TfidfVectorizer


def extract_lsi_terms(texts: Iterable[str], top_k: int = 20) -> List[str]:
    docs = [t for t in texts if t]
    if not docs:
        return []
    vec = TfidfVectorizer(ngram_range=(1, 3), max_features=5000, stop_words="english")
    X = vec.fit_transform(docs)
    # Rank features by sum tf-idf
    scores = X.sum(axis=0).A1
    feats = vec.get_feature_names_out()
    idx = scores.argsort()[::-1][:top_k]
    return [feats[i] for i in idx]

