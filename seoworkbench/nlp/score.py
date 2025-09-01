from __future__ import annotations

from typing import Iterable, List

from .lsi import extract_lsi_terms


def nlp_optimization_score(article_text: str, target_entities: Iterable[str]) -> tuple[float, List[str], List[str]]:
    target = [t.lower() for t in target_entities if t]
    if not target:
        return 0.0, [], []

    found = []
    missing = []
    lower = article_text.lower()
    for ent in target:
        if ent in lower:
            found.append(ent)
        else:
            missing.append(ent)

    coverage = len(found) / len(target)

    # Bonus: include top LSI terms; reward if article includes its own diverse terms
    lsi = extract_lsi_terms([article_text], top_k=30)
    diversity = min(1.0, len(lsi) / 30.0)

    score = 0.7 * coverage + 0.3 * diversity
    return score, found, missing

