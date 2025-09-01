from __future__ import annotations

from typing import Dict, List

from jinja2 import Template


ARTICLE_PROMPT_TMPL = Template(
    """
You are an expert SEO writer. Write a comprehensive, accurate, human-like article.
Topic: {{ topic }}
Tone: {{ tone }}
Audience: {{ audience or 'general readers' }}
Target length (words): {{ length }}

Use this outline if provided:
{% if outline %}
Outline:
{% for sec in outline %}
- {{ sec.heading }}: {{ sec.description or '' }}
{% endfor %}
{% else %}
Create an intuitive outline.
{% endif %}

Requirements:
- Factually accurate and current; cite sources inline as (Source: name, URL) when relevant
- Natural language, varied sentence structures, avoid fluff
- Include FAQs at the end if provided
- Optimize for entities/LSI terms (include naturally): {{ entities|join(', ') }}
- Avoid plagiarism and generic phrasing; add novel, helpful insights
- Include a concise intro and a clear conclusion

Return Markdown only.
"""
)


BRIEF_PROMPT_TMPL = Template(
    """
You are an SEO content strategist. Build a detailed content brief.
Seed or topic: {{ seed or topic }}
Target keywords: {{ keywords|join(', ') }}

Include:
- Working title and H1
- 8-14 section outline with headings and short descriptions
- 8-10 suggested FAQs (People Also Ask style)
- Suggested schema types (Article, FAQ, HowTo, etc.)
- Notes on E-E-A-T and topical gaps to fill
Return a concise JSON-like plan in Markdown.
"""
)


SOCIAL_MICROCONTENT_TMPL = Template(
    """
From the article, generate:
- 5 LinkedIn post angles (2-3 sentences each)
- 8 Tweet/X snippets (max 260 chars)
- 5 Instagram carousel slide captions (short, punchy, with a hook)
- 5 YouTube title ideas (<= 70 chars)
Keep it audience-relevant and non-repetitive.
Return as Markdown bullet lists.
"""
)


def render_article_prompt(topic: str, tone: str, audience: str | None, length: int, outline: List[dict] | None, entities: List[str]) -> str:
    return ARTICLE_PROMPT_TMPL.render(topic=topic, tone=tone, audience=audience, length=length, outline=outline, entities=entities)


def render_brief_prompt(topic: str, keywords: List[str], seed: str | None) -> str:
    return BRIEF_PROMPT_TMPL.render(topic=topic, keywords=keywords, seed=seed)


def render_social_prompt() -> str:
    return SOCIAL_MICROCONTENT_TMPL.render()

