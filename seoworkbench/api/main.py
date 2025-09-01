from __future__ import annotations

import asyncio
from typing import List

from fastapi import FastAPI, HTTPException

from ..aggregator import research_keywords
from ..models import (
    BriefRequest,
    ContentBrief,
    GenerationRequest,
    GenerationResponse,
    ResearchRequest,
    ResearchResponse,
)
from ..nlp.embeddings import EmbeddingModel
from ..nlp.clustering import cluster_embeddings, centroid
from ..schemas.generate import article_schema, faq_schema
from ..generation.generator import generate_brief, generate_article
from ..opportunity import score_record
from ..storage.db import create_all, db_session
from ..storage.models import Job, JobStatusEnum
from ..tasks import celery_app

app = FastAPI(title="SEO Workbench API", version="0.1.0")


@app.on_event("startup")
async def on_startup() -> None:
    # Create DB tables if DSN is provided
    try:
        create_all()
    except Exception:
        pass


@app.post("/keywords/research", response_model=ResearchResponse)
async def keywords_research(req: ResearchRequest) -> ResearchResponse:
    records = await research_keywords(req.seeds, max_keywords=req.max_keywords)

    # Compute opportunity on records (can incorporate real metrics when available)
    for r in records:
        r.opportunity = score_record(r)

    # Embed + cluster
    emb = EmbeddingModel()
    vecs = emb.embed([r.candidate.term for r in records])
    labels = cluster_embeddings(vecs, min_cluster_size=5)

    clusters_map = {}
    for rec, lab, vec in zip(records, labels, vecs):
        cid = f"c{lab}"
        rec.cluster_id = cid
        clusters_map.setdefault(cid, {"id": cid, "label": cid, "keywords": [], "_vecs": []})
        clusters_map[cid]["keywords"].append(rec.model_dump())
        clusters_map[cid]["_vecs"].append(vec)

    clusters = []
    for cid, data in clusters_map.items():
        c = {
            "id": data["id"],
            "label": data["label"],
            "keywords": data["keywords"],
            "centroid": centroid(data["_vecs"]),
        }
        clusters.append(c)

    return ResearchResponse(clusters=clusters)


@app.post("/content/brief", response_model=ContentBrief)
async def content_brief(req: BriefRequest) -> ContentBrief:
    topic = req.seed or (req.keywords[0] if req.keywords else "")
    brief = await generate_brief(topic=topic, keywords=req.keywords, seed=req.seed)
    return brief


@app.post("/content/generate", response_model=GenerationResponse)
async def content_generate(req: GenerationRequest) -> GenerationResponse:
    # Extract entities from brief outline as a naive target entity list
    entities: List[str] = []
    if req.brief:
        for sec in req.brief.outline:
            entities.extend(sec.target_keywords[:2])
    result = await generate_article(req, target_entities=entities[:25])

    # Schema suggestions
    if req.brief:
        schema = article_schema(result.title, req.brief.description)
        if req.brief.faqs:
            schema = {"@graph": [schema, faq_schema(req.brief.faqs)]}
        result.schema_jsonld = schema

    return result


def _uuid() -> str:
    import uuid
    return uuid.uuid4().hex


@app.post("/jobs/research")
async def jobs_research(req: ResearchRequest) -> dict:
    # Create a job and enqueue
    job = Job(id=_uuid(), type="research", status=JobStatusEnum.PENDING, payload=req.model_dump())
    with db_session() as db:
        db.add(job)
    celery_app.send_task("jobs.research", args=[job.id, req.seeds, req.max_keywords])
    return {"job_id": job.id, "status": job.status}


@app.post("/jobs/brief")
async def jobs_brief(req: BriefRequest) -> dict:
    topic = req.seed or (req.keywords[0] if req.keywords else "")
    if not topic:
        raise HTTPException(status_code=400, detail="Topic or seed required")
    job = Job(id=_uuid(), type="brief", status=JobStatusEnum.PENDING, payload=req.model_dump())
    with db_session() as db:
        db.add(job)
    celery_app.send_task("jobs.brief", args=[job.id, topic, req.keywords])
    return {"job_id": job.id, "status": job.status}


@app.post("/jobs/generate")
async def jobs_generate(req: GenerationRequest) -> dict:
    job = Job(id=_uuid(), type="generate", status=JobStatusEnum.PENDING, payload=req.model_dump())
    with db_session() as db:
        db.add(job)
    brief = req.brief.model_dump() if req.brief else None
    celery_app.send_task("jobs.generate", args=[job.id, req.topic, brief, req.target_length_words])
    return {"job_id": job.id, "status": job.status}


@app.get("/jobs/{job_id}")
async def jobs_status(job_id: str) -> dict:
    with db_session() as db:
        job = db.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return {
            "job_id": job.id,
            "type": job.type,
            "status": job.status,
            "result": job.result,
            "error": job.error,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        }

