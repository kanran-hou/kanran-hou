"""智谱 GLM-4 API Provider（占位，可选接入）"""

from __future__ import annotations

import httpx

from app.services.llm.client import LLMClient


class GLMProvider(LLMClient):
    """智谱 GLM-4 API 适配（预留，接口逻辑与 DeepSeek 类似）"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://open.bigmodel.cn/api/paas/v4",
        model: str = "glm-4-plus",
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
