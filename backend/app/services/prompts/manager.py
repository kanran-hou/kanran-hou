"""Prompt 版本管理 — 注册、获取、热更新"""

from __future__ import annotations

from app.services.prompts.base import PromptTemplate
from app.services.prompts.xiaohongshu import xiaohongshu_prompt
from app.services.prompts.ecommerce import ecommerce_prompt
from app.services.prompts.local_tourism import local_tourism_prompt
from app.services.prompts.short_video import short_video_prompt


class PromptNotFoundError(KeyError):
    """指定赛道 Prompt 未注册"""


class PromptManager:
    """Prompt 管理器：注册 + 按赛道获取 + 热更新预留"""

    def __init__(self) -> None:
        self._registry: dict[str, PromptTemplate] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(xiaohongshu_prompt)
        self.register(ecommerce_prompt)
        self.register(local_tourism_prompt)
        self.register(short_video_prompt)

    def register(self, template: PromptTemplate) -> None:
        self._registry[template.track_type] = template

    def get(self, track_type: str) -> PromptTemplate:
        prompt = self._registry.get(track_type)
        if prompt is None:
            raise PromptNotFoundError(
                f"未找到赛道 '{track_type}' 的 Prompt 模板"
            )
        return prompt

    def list_tracks(self) -> list[dict]:
        return [t.to_dict() for t in self._registry.values()]

    def update(self, track_type: str, template: PromptTemplate) -> None:
        """热更新：运行时替换指定赛道的 Prompt"""
        self._registry[track_type] = template


_manager: PromptManager | None = None


def get_prompt_manager() -> PromptManager:
    global _manager
    if _manager is None:
        _manager = PromptManager()
    return _manager
