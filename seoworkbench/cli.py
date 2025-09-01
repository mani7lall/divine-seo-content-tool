from __future__ import annotations

import asyncio
import json
from typing import List

import typer

from .aggregator import research_keywords
from .models import BriefRequest, GenerationRequest
from .nlp.embeddings import EmbeddingModel
from .nlp.clustering import cluster_embeddings, centroid
from .generation.generator import generate_brief, generate_article

app = typer.Typer(add_completion=False, help="SEO Workbench CLI")


@app.command()
def research(seed: List[str] = typer.Option(..., "--seed", help="Seed keywords"), max_keywords: int = 200):
    """Discover and cluster keywords for the given seeds."""
    async def _run():
        records = await research_keywords(seed, max_keywords=max_keywords)
        emb = EmbeddingModel()
        vecs = emb.embed([r.candidate.term for r in records])
        labels = cluster_embeddings(vecs, min_cluster_size=5)
        clusters = {}
        for rec, lab, vec in zip(records, labels, vecs):
            cid = f"c{lab}"
            rec.cluster_id = cid
            clusters.setdefault(cid, {"id": cid, "label": cid, "keywords": [], "_vecs": []})
            clusters[cid]["keywords"].append(rec.model_dump())
            clusters[cid]["_vecs"].append(vec)
        out = []
        for cid, data in clusters.items():
            out.append({
                "id": cid,
                "label": cid,
                "keywords": data["keywords"],
                "centroid": centroid(data["_vecs"]),
            })
        print(json.dumps({"clusters": out}, ensure_ascii=False, indent=2))

    asyncio.run(_run())


@app.command()
def brief(topic: str = typer.Argument(...), keywords: List[str] = typer.Option([], "--kw")):
    """Generate an SEO brief for a topic and optional keywords."""
    async def _run():
        b = await generate_brief(topic=topic, keywords=keywords, seed=topic)
        print(json.dumps(b.model_dump(), ensure_ascii=False, indent=2))

    asyncio.run(_run())


@app.command()
def generate(topic: str = typer.Argument(...), target_length_words: int = 1800):
    """Generate a long-form article for a topic."""
    async def _run():
        req = GenerationRequest(topic=topic, target_length_words=target_length_words)
        res = await generate_article(req, target_entities=[topic])
        print(json.dumps(res.model_dump(), ensure_ascii=False))

    asyncio.run(_run())


if __name__ == "__main__":
    app()

