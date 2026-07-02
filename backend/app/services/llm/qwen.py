"""通义千问 API Provider（兼容 OpenAI 格式）"""

from __future__ import annotations

import httpx

from app.services.llm.client import LLMClient


class QwenProvider(LLMClient):
    """通义千问 qwen-max API 适配"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        model: str = "qwen-max",
        timeout: int = 60,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
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
        resp = await self._client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def check_health(self) -> bool:
        try:
            await self.chat(
                [{"role": "user", "content": "hi"}],
                max_tokens=2,
            )
            return True
        except Exception:
            return False

    async def close(self) -> None:
        await self._client.aclose()
