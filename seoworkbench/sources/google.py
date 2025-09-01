from __future__ import annotations

import asyncio
from typing import List

import httpx

from ..config import get_settings
from ..models import KeywordCandidate, SERPResult
from .base import SearchSource


class GoogleLikeSource(SearchSource):
    name = "google_like"

    def __init__(self) -> None:
        self.settings = get_settings()

    async def fetch_autocomplete(self, seed: str) -> List[KeywordCandidate]:
        # Prefer SearxNG if provided, as it can proxy multiple engines via an API-friendly interface
        if self.settings.SEARXNG_BASE_URL:
            url = f"{self.settings.SEARXNG_BASE_URL.rstrip('/')}/autocomplete?q={httpx.QueryParams({'q': seed}).get('q')}"
            async with httpx.AsyncClient(timeout=20) as client:
                try:
                    r = await client.get(url)
                    r.raise_for_status()
                    data = r.json()
                    return [KeywordCandidate(term=s, source=self.name) for s in data[:20] if isinstance(s, str)]
                except Exception:
                    return []
        # As a generic fallback, return seeded variations (programmatic modifiers)
        base = seed.strip()
        mods = [
            "best", "top", "cheap", "near me", "for beginners", "vs", "review",
            "2025", "how to", "guide", "comparison", "alternatives", "pros and cons",
        ]
        return [KeywordCandidate(term=f"{base} {m}", source=self.name, modifiers=[m]) for m in mods]

    async def fetch_people_also_ask(self, seed: str) -> List[KeywordCandidate]:
        # Placeholder: With SerpAPI or other providers, you can fetch PAA explicitly.
        # Here we synthesize likely PAA-style questions.
        qmods = [
            "What is", "How does", "Is it worth", "How much", "How long", "Which is better",
            "Can you", "Why is", "When should", "Where to",
        ]
        return [KeywordCandidate(term=f"{qm} {seed}?".strip(), source=self.name, intent="informational") for qm in qmods]

    async def fetch_related(self, seed: str) -> List[KeywordCandidate]:
        # If a compliant API is configured, query it here. For now, synthesize related patterns.
        base = seed.strip()
        rels = [
            f"{base} alternatives",
            f"{base} vs competitors",
            f"{base} pricing",
            f"{base} features",
            f"{base} problems",
            f"{base} benefits",
        ]
        return [KeywordCandidate(term=r, source=self.name) for r in rels]

    async def fetch_serp(self, query: str, top_n: int = 10) -> List[SERPResult]:
        settings = self.settings
        results: List[SERPResult] = []

        # Example: Google Custom Search API
        if settings.GOOGLE_CSE_API_KEY and settings.GOOGLE_CSE_CX:
            params = {
                "key": settings.GOOGLE_CSE_API_KEY,
                "cx": settings.GOOGLE_CSE_CX,
                "q": query,
                "num": min(top_n, 10),
            }
            async with httpx.AsyncClient(timeout=30) as client:
                try:
                    r = await client.get("https://www.googleapis.com/customsearch/v1", params=params)
                    r.raise_for_status()
                    data = r.json()
                    for idx, item in enumerate(data.get("items", []), start=1):
                        results.append(
                            SERPResult(
                                title=item.get("title", ""),
                                url=item.get("link", ""),
                                snippet=item.get("snippet"),
                                rank=idx,
                                source=self.name,
                            )
                        )
                    return results
                except Exception:
                    return results

        # Otherwise, return empty list (or synthetic stubs) to avoid scraping.
        return results


async def gather_all(source: GoogleLikeSource, seed: str) -> List[KeywordCandidate]:
    ac_task = source.fetch_autocomplete(seed)
    paa_task = source.fetch_people_also_ask(seed)
    rel_task = source.fetch_related(seed)
    ac, paa, rel = await asyncio.gather(ac_task, paa_task, rel_task)
    return ac + paa + rel

