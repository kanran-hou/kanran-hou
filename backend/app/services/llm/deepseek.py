"""DeepSeek Chat API Provider"""

from __future__ import annotations

from typing import Any

import httpx
from loguru import logger

from app.config import settings
from app.services.llm.client import LLMClient


class DeepSeekProvider(LLMClient):
    """DeepSeek Chat API 适配"""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int = 60,
    ) -> None:
        self.api_key = api_key or settings.AI_API_KEY
        self.base_url = (base_url or settings.AI_API_BASE).rstrip("/")
        self.model = model or settings.AI_MODEL
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout, connect=10.0),
            headers={"Authorization": f"Bearer {self.api_key}"},
        )

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        resp = await self._client.post("/v1/chat/completions", json=payload)
        resp = await self._client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def check_health(self) -> bool:
        try:
            resp = await self._client.get("/v1/models", timeout=5.0)
            return resp.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        await self._client.aclose()
