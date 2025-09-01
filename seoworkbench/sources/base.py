from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..models import KeywordCandidate, SERPResult


class SearchSource(ABC):
    name: str = "base"

    @abstractmethod
    async def fetch_autocomplete(self, seed: str) -> List[KeywordCandidate]:
        raise NotImplementedError

    @abstractmethod
    async def fetch_people_also_ask(self, seed: str) -> List[KeywordCandidate]:
        raise NotImplementedError

    @abstractmethod
    async def fetch_related(self, seed: str) -> List[KeywordCandidate]:
        raise NotImplementedError

    @abstractmethod
    async def fetch_serp(self, query: str, top_n: int = 10) -> List[SERPResult]:
        raise NotImplementedError

