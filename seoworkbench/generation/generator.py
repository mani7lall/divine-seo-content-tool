from __future__ import annotations

from typing import Dict, List, Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import get_settings
from ..models import ContentBrief, GenerationRequest, GenerationResponse
from ..nlp.score import nlp_optimization_score
from .prompts import render_article_prompt, render_brief_prompt, render_social_prompt


class LLMProvider:
    async def complete(self, prompt: str, *, max_tokens: int = 2048) -> str:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model = model

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def complete(self, prompt: str, *, max_tokens: int = 2048) -> str:
        # Chat Completions API usage
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return resp.choices[0].message.content or ""


class OllamaProvider(LLMProvider):
    def __init__(self, host: str, model: str) -> None:
        self.host = host.rstrip("/")
        self.model = model

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def complete(self, prompt: str, *, max_tokens: int = 2048) -> str:
        import httpx
        payload = {"model": self.model, "prompt": prompt}
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(f"{self.host}/api/generate", json=payload)
            r.raise_for_status()
            data = r.json()
            return data.get("response", "")


class StubProvider(LLMProvider):
    async def complete(self, prompt: str, *, max_tokens: int = 2048) -> str:
        # Deterministic stub for offline/dev usage
        return "This is a placeholder response. Configure OPENAI or OLLAMA to get real content.\n\n# Introduction\n...\n\n# Section 1\n...\n\n# Conclusion\n..."


async def resolve_provider(role: str = "writing") -> LLMProvider:
    s = get_settings()
    choice = s.LLM_PROVIDER_WRITING if role == "writing" else s.LLM_PROVIDER_RESEARCH
    try:
        if choice == "perplexity" and s.PERPLEXITY_API_KEY:
            from ..providers.perplexity import PerplexityProvider
            return PerplexityProvider(s.PERPLEXITY_API_KEY, s.PERPLEXITY_MODEL)  # type: ignore[return-value]
        if choice == "gemini" and s.GEMINI_API_KEY:
            from ..providers.gemini import GeminiProvider
            return GeminiProvider(s.GEMINI_API_KEY, s.GEMINI_MODEL)  # type: ignore[return-value]
        if choice == "openrouter" and s.OPENROUTER_API_KEY:
            from ..providers.openrouter import OpenRouterProvider
            return OpenRouterProvider(s.OPENROUTER_API_KEY, s.OPENROUTER_MODEL)  # type: ignore[return-value]
        if choice == "openai" and s.OPENAI_API_KEY:
            return OpenAIProvider(s.OPENAI_API_KEY, s.OPENAI_MODEL)
        if choice == "ollama" and s.OLLAMA_HOST:
            return OllamaProvider(s.OLLAMA_HOST, s.OLLAMA_MODEL)
    except Exception:
        pass
    # Fallbacks
    if s.OPENAI_API_KEY:
        return OpenAIProvider(s.OPENAI_API_KEY, s.OPENAI_MODEL)
    if s.OLLAMA_HOST:
        return OllamaProvider(s.OLLAMA_HOST, s.OLLAMA_MODEL)
    return StubProvider()


async def generate_brief(topic: str, keywords: List[str], seed: Optional[str]) -> ContentBrief:
    provider = await resolve_provider(role="research")
    prompt = render_brief_prompt(topic=topic, keywords=keywords, seed=seed)
    raw = await provider.complete(prompt, max_tokens=1200)

    # Heuristic parse of Markdown-like output into a structured brief
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    title = next((l.replace("Title:", "").strip() for l in lines if l.lower().startswith("title:")), f"{topic} (Brief)")
    h1 = next((l.replace("H1:", "").strip() for l in lines if l.lower().startswith("h1:")), title)
    faqs = [l[2:].strip() for l in lines if l.startswith("-") and "?" in l]

    outline = []
    for l in lines:
        if l.startswith("-") and "?" not in l:
            outline.append({"heading": l[1:].strip(), "description": ""})

    return ContentBrief(
        title=title,
        h1=h1,
        outline=[
            # Coerce into BriefSection model schema implicitly by FastAPI/Pydantic later
            {"heading": sec["heading"], "description": sec.get("description", ""), "target_keywords": keywords[:5]}
            for sec in outline[:12]
        ],
        faqs=faqs[:10],
        schema_suggestions=["Article", "FAQ"],
        internal_link_suggestions=[],
    )


async def generate_article(req: GenerationRequest, target_entities: List[str]) -> GenerationResponse:
    provider = await resolve_provider(role="writing")
    outline = [s.model_dump() for s in (req.brief.outline if req.brief else [])]
    prompt = render_article_prompt(
        topic=req.topic,
        tone=req.tone,
        audience=req.audience,
        length=req.target_length_words,
        outline=outline or None,
        entities=target_entities,
    )
    md = await provider.complete(prompt, max_tokens=4096)

    nlp_score, covered, missing = nlp_optimization_score(md, target_entities)

    # Basic microcontent generation (can be LLM-backed later)
    social_prompt = render_social_prompt()
    social_md = await provider.complete(social_prompt, max_tokens=1000)
    micro = {
        "linkedin": [l[2:].strip() for l in social_md.splitlines() if l.strip().startswith("-")][:5],
        "twitter": [],
    }

    return GenerationResponse(
        title=req.brief.title if req.brief and req.brief.title else req.topic,
        article_markdown=md,
        nlp_score=nlp_score,
        schema_jsonld=None,
        microcontent=micro,
    )

