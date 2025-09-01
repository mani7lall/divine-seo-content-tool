from __future__ import annotations

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class GeminiProvider:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
    async def complete(self, prompt: str, *, max_tokens: int = 2048) -> str:
        params = {"key": self.api_key}
        # Gemini expects a structured content payload
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7},
        }
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(self.base_url, params=params, json=payload)
            r.raise_for_status()
            data = r.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                return ""

