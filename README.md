# SEO Workbench (Programmatic SEO & Content Automation)

An end-to-end, modular SEO research and content generation platform inspired by SurferSEO, Frase, Clearscope, and modern programmatic SEO. Input a keyword or URL; output clustered keywords, data-driven briefs, optimized long-form content, microcontent, schemas, and internal linking suggestions.

Key pillars:
- Multi-source keyword discovery (SERP, autocomplete, PAA, related queries) via pluggable adapters
- NLP-driven clustering and topic mapping (embeddings + clustering)
- Brief generation with SERP decomposition, FAQ, schema suggestions
- Long-form draft generation with provider-agnostic LLM interface (OpenAI/Ollama/HF)
- Microcontent and JSON-LD schema generation
- REST API (FastAPI) + CLI (Typer)

## Quickstart (Windows PowerShell)

Environment strategy (free tiers):
- Frontend: Cloudflare Pages (Next.js + next-on-pages)
- Backend API: Fly.io (FastAPI container)
- Worker: Fly.io (Celery container)
- DB: Neon (serverless Postgres)
- Cache/Queues: Upstash Redis

```bash path=null start=null
# 1) Create and activate venv
python -m venv .venv
. .venv\Scripts\Activate.ps1

# 2) Install dependencies
pip install -r requirements.txt

# 3) Configure environment
Copy-Item .env.example .env
# Edit .env to add keys as needed (e.g., OPENAI_API_KEY, SERPAPI_API_KEY, etc.)

# 4) Run the API
uvicorn seoworkbench.api.main:app --reload --host 0.0.0.0 --port 8000

# 5) Try the CLI
python -m seoworkbench.cli research --seed "best hiking backpacks"
```

Notes:
- Do not put secrets in code or commit them; use environment variables (.env is git-ignored).
- This repo includes API-friendly stubs for search data. Use official APIs (e.g., SerpAPI, Custom Search, SearxNG) to comply with terms of service.

## Environment Variables
See .env.example for all supported settings. Common keys:
- OPENAI_API_KEY, OPENAI_MODEL
- OLLAMA_HOST, OLLAMA_MODEL
- HUGGINGFACE_API_KEY, HF_EMBEDDING_MODEL
- SERPAPI_API_KEY (if using SerpAPI)
- GOOGLE_CSE_API_KEY, GOOGLE_CSE_CX (if using Google Custom Search)
- SEARXNG_BASE_URL (if using a compliant metasearch instance)

## High-Level Architecture
- seoworkbench/
  - config.py: Settings and feature flags
  - models.py: Pydantic models for keywords, clusters, briefs, content
  - sources/: Data source adapters (Google, etc.)
  - aggregator.py: Multi-source expansion, dedupe, normalization
  - nlp/: Embeddings, LSI/entity extraction, clustering, scoring
  - generation/: Prompt templates and provider-agnostic LLM generator
  - schemas/: JSON-LD helpers
  - internal_linking.py: Cross-page link suggestions
  - api/: FastAPI app and endpoints
  - cli.py: Typer CLI

## API Endpoints (initial)

Jobs (async):
- POST /jobs/research, /jobs/brief, /jobs/generate, and GET /jobs/{id}
- POST /keywords/research: discover and cluster keywords
- POST /content/brief: build a content brief from keywords/cluster
- POST /content/generate: generate long-form content + microcontent + schema

## Deployment (Cloudflare Pages + Fly.io)

1) Create external services
- Neon Postgres (copy the connection URI) and Upstash Redis (copy the URL)
- Fly.io: create two apps (API, Worker) or use the provided fly.api.toml and fly.worker.toml

2) Set env variables (runtime)
- API/Worker (Fly.io secrets):
  - POSTGRES_DSN, REDIS_URL
  - LLM_PROVIDER_RESEARCH, LLM_PROVIDER_WRITING
  - PERPLEXITY_API_KEY, PERPLEXITY_MODEL (for research)
  - OPENROUTER_API_KEY, OPENROUTER_MODEL (for writing) OR GEMINI_API_KEY/GEMINI_MODEL

3) Cloudflare Pages
- Connect your GitHub repo to a new Pages project (divine-seo-content-tool)
- Framework preset: Next.js
- Build command: npm ci && npm run build (in dashboard)
- Output directory: dashboard/.vercel/output/static
- Set NEXT_PUBLIC_API_BASE_URL to your Fly.io API URL (e.g., https://divine-seo-content-tool-api.fly.dev)

4) GitHub Actions (optional CI/CD)
- Set repository secrets: FLY_API_TOKEN, CF_API_TOKEN, CF_ACCOUNT_ID
- The provided workflows build/deploy automatically on push to main.

## Roadmap
- Add more data sources (trends, more SERP providers)
- Add advanced scoring (SERP overlap, topical gaps, passage ranking signals)
- Add background jobs & persistence (Postgres/Redis, Celery)
- Add dashboard UI (Next.js) and CMS integrations
- Extend programmatic SEO page generation (bulk modifiers, templating)

## Legal & Compliance
- Use official APIs where required. Scraping engines directly may violate terms.
- Ensure generated content is reviewed for factual accuracy and compliance.
- Handle secrets strictly via environment variables.

