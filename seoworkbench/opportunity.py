from __future__ import annotations

from typing import Optional

from .models import KeywordRecord


def _norm(value: Optional[float], max_value: float, default: float = 0.0) -> float:
    if value is None:
        value = default
    value = max(0.0, min(value, max_value))
    return value / max_value


def score_record(rec: KeywordRecord) -> float:
    """Heuristic opportunity score 0..1.

    Combines:
    - volume (proxy-capped at 50k if provided)
    - KD (lower is better)
    - trend score (0..1)
    - long-tail bonus (more tokens => slight boost)
    """
    # Normalized signals
    vol = _norm(float(rec.metrics.volume) if rec.metrics.volume is not None else None, max_value=50000.0, default=0.0)
    kd = _norm(float(rec.metrics.kd) if rec.metrics.kd is not None else None, max_value=100.0, default=50.0)
    trend = rec.metrics.trend_score if rec.metrics.trend_score is not None else 0.5
    if trend < 0:
        trend = 0.0
    if trend > 1:
        trend = 1.0

    # Long-tail bonus: terms with >2 tokens get a boost up to +0.2
    tokens = len(rec.candidate.term.split())
    longtail_bonus = min(0.2, max(0.0, (tokens - 2) * 0.05))

    # Weighted sum
    score = 0.4 * vol + 0.3 * (1.0 - kd) + 0.2 * trend + 0.1 * (longtail_bonus / 0.2)
    return max(0.0, min(score, 1.0))

