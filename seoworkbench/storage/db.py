from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from ..config import get_settings

Base = declarative_base()

_engine = None
_SessionLocal: Optional[sessionmaker] = None


def init_engine() -> None:
    global _engine, _SessionLocal
    dsn = get_settings().POSTGRES_DSN
    if not dsn:
        return
    _engine = create_engine(dsn, pool_pre_ping=True, future=True)
    _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False, future=True)


def create_all() -> None:
    if _engine is None:
        init_engine()
    if _engine is not None:
        Base.metadata.create_all(bind=_engine)


@contextmanager
def db_session() -> Generator[Session, None, None]:
    if _SessionLocal is None:
        init_engine()
    if _SessionLocal is None:
        # Fallback: yield a dummy session context that raises if used
        raise RuntimeError("Database is not configured. Set POSTGRES_DSN.")
    session: Session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

