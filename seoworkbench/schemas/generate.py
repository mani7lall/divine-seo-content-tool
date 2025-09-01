from __future__ import annotations

from typing import Any, Dict, List


def article_schema(headline: str, description: str | None, url: str | None = None) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": headline,
    }
    if description:
        data["description"] = description
    if url:
        data["url"] = url
    return data


def faq_schema(questions: List[str]) -> Dict[str, Any]:
    items = [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": ""},
        }
        for q in questions
    ]
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": items,
    }

