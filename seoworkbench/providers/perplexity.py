from __future__ import annotations

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class PerplexityProvider:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.perplexity.ai/chat/completions"

    @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
    async def complete(self, prompt: str, *, max_tokens: int = 2048) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(self.base_url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            # OpenAI-compatible shape
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")

