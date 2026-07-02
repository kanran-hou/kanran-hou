"""Prompt 模板结构定义"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass
class PromptTemplate:
    """单个赛道 Prompt 模板"""

    track_type: str
    system_prompt: str
    user_prompt_template: str
    weights: dict[str, float] = field(default_factory=lambda: {
        "title": 0.25,
        "emotion": 0.25,
        "structure": 0.25,
        "audience": 0.25,
    })
    version: str = "1.0"

    def build_messages(self, text: str) -> list[dict[str, str]]:
        """构建完整的 messages 列表（system + user）"""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt_template.format(text=text)},
        ]

    def to_dict(self) -> dict:
        return {
            "track_type": self.track_type,
            "version": self.version,
            "weights": self.weights,
        }
