from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from celery import Celery

from .config import get_settings
from .aggregator import research_keywords
from .generation.generator import generate_brief, generate_article
from .models import BriefRequest, GenerationRequest
from .storage.db import db_session
from .storage.models import Job, JobStatusEnum


settings = get_settings()

celery_app = Celery(
    "seoworkbench",
    broker=settings.REDIS_URL or "redis://localhost:6379/0",
    backend=settings.REDIS_URL or "redis://localhost:6379/0",
)


def _update_job(job_id: str, **changes: Any) -> None:
    with db_session() as db:
        job = db.get(Job, job_id)
        if not job:
            return
        for k, v in changes.items():
            setattr(job, k, v)
        job.updated_at = datetime.utcnow()
        db.add(job)


@celery_app.task(name="jobs.research")
def task_research(job_id: str, seeds: List[str], max_keywords: int = 300) -> Dict[str, Any]:
    _update_job(job_id, status=JobStatusEnum.STARTED)
    try:
        records = _run_async(research_keywords(seeds, max_keywords=max_keywords))
        payload = {"seeds": seeds, "max_keywords": max_keywords}
        result = {"keywords": [r.candidate.term for r in records]}
        _update_job(job_id, status=JobStatusEnum.SUCCESS, result=result)
        return result
    except Exception as e:
        _update_job(job_id, status=JobStatusEnum.FAILURE, error=str(e))
        raise


@celery_app.task(name="jobs.brief")
def task_brief(job_id: str, topic: str, keywords: List[str]) -> Dict[str, Any]:
    _update_job(job_id, status=JobStatusEnum.STARTED)
    try:
        brief = _run_async(generate_brief(topic=topic, keywords=keywords, seed=topic))
        result = brief.model_dump()
        _update_job(job_id, status=JobStatusEnum.SUCCESS, result=result)
        return result
    except Exception as e:
        _update_job(job_id, status=JobStatusEnum.FAILURE, error=str(e))
        raise


@celery_app.task(name="jobs.generate")
def task_generate(job_id: str, topic: str, brief: Optional[Dict[str, Any]] = None, length: int = 1800) -> Dict[str, Any]:
    _update_job(job_id, status=JobStatusEnum.STARTED)
    try:
        req = GenerationRequest(topic=topic, brief=brief, target_length_words=length)
        result_obj = _run_async(generate_article(req, target_entities=[topic]))
        result = result_obj.model_dump()
        _update_job(job_id, status=JobStatusEnum.SUCCESS, result=result)
        return result
    except Exception as e:
        _update_job(job_id, status=JobStatusEnum.FAILURE, error=str(e))
        raise


def _run_async(coro):
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        return coro  # Should not occur in worker
    return loop.run_until_complete(coro)

