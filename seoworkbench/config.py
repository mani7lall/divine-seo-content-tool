from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Provider selection
    LLM_PROVIDER_RESEARCH: str = Field(default="perplexity")
    LLM_PROVIDER_WRITING: str = Field(default="openrouter")

    # OpenAI (optional)
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")

    # Perplexity
    PERPLEXITY_API_KEY: str | None = None
    PERPLEXITY_MODEL: str = Field(default="sonar-large-online")

    # Gemini
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = Field(default="gemini-2.5-pro")

    # OpenRouter
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_MODEL: str = Field(default="deepseek/deepseek-r1:free")

    # Ollama (optional)
    OLLAMA_HOST: str | None = None
    OLLAMA_MODEL: str = Field(default="llama3.1:8b")

    HUGGINGFACE_API_KEY: str | None = None
    HF_EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")

    SERPAPI_API_KEY: str | None = None
    GOOGLE_CSE_API_KEY: str | None = None
    GOOGLE_CSE_CX: str | None = None
    SEARXNG_BASE_URL: str | None = None

    MAX_WORKERS: int = 8

    # Persistence and queues
    POSTGRES_DSN: str | None = None  # e.g., postgresql+psycopg://user:pass@host:5432/db
    REDIS_URL: str | None = None  # e.g., redis://redis:6379/0

    HTTP_PROXY: str | None = None
    HTTPS_PROXY: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]

