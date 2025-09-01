from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Tuple


def suggest_internal_links(pages: Dict[str, Iterable[str]], top_k: int = 5) -> Dict[str, List[Tuple[str, int]]]:
    # pages: {page_id: [keywords...]}
    idx = {pid: set(kw.lower().strip() for kw in kws if kw) for pid, kws in pages.items()}
    out: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
    for a, kwa in idx.items():
        scores = []
        for b, kwb in idx.items():
            if a == b:
                continue
            overlap = len(kwa & kwb)
            if overlap > 0:
                scores.append((b, overlap))
        scores.sort(key=lambda x: x[1], reverse=True)
        out[a] = scores[:top_k]
    return out

