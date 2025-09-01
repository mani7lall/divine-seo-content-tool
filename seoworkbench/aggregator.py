from __future__ import annotations

import asyncio
from typing import Iterable, List

from .models import KeywordCandidate, KeywordRecord, KeywordMetrics, SERPResult
from .sources.google import GoogleLikeSource, gather_all
from .generation.generator import resolve_provider


PROGRAMMATIC_MODIFIERS = [
    # intent
    "how to", "what is", "vs", "best", "top", "review", "alternatives",
    # audience
    "for beginners", "for experts", "for students", "for small business",
    # location (example placeholders)
    "near me", "in usa", "in uk", "in canada",
    # pain points
    "problems", "issues", "risks", "mistakes",
]


def expand_programmatically(seed: str) -> List[KeywordCandidate]:
    seed = seed.strip()
    out: List[KeywordCandidate] = []
    for mod in PROGRAMMATIC_MODIFIERS:
        out.append(KeywordCandidate(term=f"{seed} {mod}", source="programmatic", modifiers=[mod]))
    return out


async def research_keywords(seeds: Iterable[str], max_keywords: int = 300) -> List[KeywordRecord]:
    source = GoogleLikeSource()

    async def llm_expand(seed: str) -> List[KeywordCandidate]:
        # Use the research provider to generate additional long-tail variants without scraping
        provider = await resolve_provider(role="research")
        prompt = (
            f"Generate 50 long-tail keyword variations for: '{seed}'.\n"
            "Mix intents (informational, transactional, comparison), audiences, locations, and pain points.\n"
            "Return one variant per line, no numbering."
        )
        text = await provider.complete(prompt, max_tokens=800)
        cands = []
        for line in text.splitlines():
            t = line.strip().lstrip("- ")
            if len(t) >= 3:
                cands.append(KeywordCandidate(term=t, source="llm"))
        return cands[:50]

    async def per_seed(seed: str) -> List[KeywordCandidate]:
        collected = await gather_all(source, seed)
        collected += expand_programmatically(seed)
        try:
            collected += await llm_expand(seed)
        except Exception:
            pass
        return collected

    # Collect
    buckets = await asyncio.gather(*[per_seed(s) for s in seeds])
    candidates = [c for bucket in buckets for c in bucket]

    # Dedupe by term, simple normalization
    seen = set()
    uniq: List[KeywordCandidate] = []
    for c in candidates:
        t = c.term.lower().strip()
        if t not in seen:
            uniq.append(c)
            seen.add(t)

    # Limit
    uniq = uniq[:max_keywords]

    # Build records and fetch (optional) SERP top for a sample subset
    records: List[KeywordRecord] = [
        KeywordRecord(candidate=c, metrics=KeywordMetrics(), serp_top=[]) for c in uniq
    ]

    # Optionally enrich some entries with SERP top
    subset = records[: min(20, len(records))]
    serp_tasks = [source.fetch_serp(r.candidate.term, top_n=10) for r in subset]
    serp_results = await asyncio.gather(*serp_tasks)
    for rec, serp in zip(subset, serp_results):
        rec.serp_top = serp

    return records

