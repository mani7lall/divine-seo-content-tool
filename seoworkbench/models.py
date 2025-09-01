from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class KeywordCandidate(BaseModel):
    term: str
    source: str = Field(default="unknown")
    intent: Optional[str] = None  # informational, commercial, navigational, transactional
    modifiers: List[str] = Field(default_factory=list)


class SERPResult(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None
    rank: Optional[int] = None
    source: str = Field(default="serp")


class KeywordMetrics(BaseModel):
    volume: Optional[int] = None
    kd: Optional[float] = None
    cpc: Optional[float] = None
    trend_score: Optional[float] = None  # 0..1


class KeywordRecord(BaseModel):
    candidate: KeywordCandidate
    metrics: KeywordMetrics = Field(default_factory=KeywordMetrics)
    serp_top: List[SERPResult] = Field(default_factory=list)
    cluster_id: Optional[str] = None
    opportunity: Optional[float] = None  # computed later


class KeywordCluster(BaseModel):
    id: str
    label: str
    keywords: List[KeywordRecord]
    centroid: Optional[List[float]] = None


class BriefSection(BaseModel):
    heading: str
    description: Optional[str] = None
    target_keywords: List[str] = Field(default_factory=list)


class ContentBrief(BaseModel):
    title: str
    description: Optional[str] = None
    h1: Optional[str] = None
    outline: List[BriefSection] = Field(default_factory=list)
    faqs: List[str] = Field(default_factory=list)
    schema_suggestions: List[str] = Field(default_factory=list)
    internal_link_suggestions: List[str] = Field(default_factory=list)


class GenerationRequest(BaseModel):
    topic: str
    brief: Optional[ContentBrief] = None
    target_length_words: int = 1800
    tone: str = "expert yet friendly"
    audience: Optional[str] = None


class GenerationResponse(BaseModel):
    title: str
    article_markdown: str
    nlp_score: Optional[float] = None
    schema_jsonld: Optional[Dict[str, Any]] = None
    microcontent: Dict[str, List[str]] = Field(default_factory=dict)


class ResearchRequest(BaseModel):
    seeds: List[str]
    max_keywords: int = 300


class ResearchResponse(BaseModel):
    clusters: List[KeywordCluster]


class BriefRequest(BaseModel):
    keywords: List[str]
    seed: Optional[str] = None


class NLPScore(BaseModel):
    score: float
    covered_entities: List[str] = Field(default_factory=list)
    missing_entities: List[str] = Field(default_factory=list)

