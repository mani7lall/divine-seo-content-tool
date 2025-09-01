from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Column, DateTime, Enum, JSON, String, Text

from .db import Base


class JobStatusEnum(str):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(64), primary_key=True)
    type = Column(String(32), nullable=False)
    status = Column(String(16), default=JobStatusEnum.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    payload = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)

