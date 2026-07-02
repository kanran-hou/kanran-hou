"""LLM 客户端基类 — 统一 request/response 接口"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMClient(ABC):
    """大模型调用基类"""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """发送对话请求，返回模型回复文本"""
        ...

    @abstractmethod
    async def check_health(self) -> bool:
        """检查 Provider 是否可用"""
        ...
