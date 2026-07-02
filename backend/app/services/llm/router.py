"""Provider 自动切换路由 — 主用 → 备用 → 降级报错"""

from __future__ import annotations

from typing import Sequence

from loguru import logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings
from app.services.llm.client import LLMClient
from app.services.llm.deepseek import DeepSeekProvider
from app.services.llm.qwen import QwenProvider


class AllProvidersFailedError(Exception):
    """所有 Provider 均不可用"""


class LLMRouter:
    """Provider 路由：自动切换 + 重试"""

    def __init__(self, providers: Sequence[LLMClient] | None = None) -> None:
        self._providers = list(providers) if providers else self._default_providers()
        self._current = 0

    @staticmethod
    def _default_providers() -> list[LLMClient]:
        providers: list[LLMClient] = []
        if settings.AI_API_KEY:
            providers.append(DeepSeekProvider())
        # 备用 Provider 需要额外配置 QWEN_API_KEY
        # if os.getenv("QWEN_API_KEY"):
        #     providers.append(QwenProvider(api_key=os.getenv("QWEN_API_KEY")))
        if not providers:
            # 无 API Key 时用 Mock Provider 供测试
            providers.append(MockProvider())
        return providers

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    )
    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """依次尝试各 Provider，全部失败则抛异常"""
        last_exc: Exception | None = None
        for i in range(len(self._providers)):
            idx = (self._current + i) % len(self._providers)
            provider = self._providers[idx]
            try:
                result = await provider.chat(
                    messages, temperature=temperature, max_tokens=max_tokens
                )
                # 成功则更新当前索引，下次从此开始
                self._current = idx
                return result
            except Exception as e:
                logger.warning(
                    "Provider {idx} ({name}) failed: {e}",
                    idx=idx,
                    name=type(provider).__name__,
                    e=e,
                )
                last_exc = e
        raise AllProvidersFailedError(
            f"所有 Provider 均不可用，最后错误：{last_exc}"
        ) from last_exc


class MockProvider(LLMClient):
    """Mock Provider — 无 API Key 时返回模拟数据供开发测试"""

    def __init__(self) -> None:
        self._call_count = 0

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        self._call_count += 1
        import json
        return json.dumps(MOCK_ANALYSIS_RESULT, ensure_ascii=False, indent=2)

    async def check_health(self) -> bool:
        return True


MOCK_ANALYSIS_RESULT = {
    "title_analysis": {
        "has_number": True,
        "has_question": False,
        "has_benefit_words": True,
        "has_emotion_hook": True,
        "score": 85,
        "comment": "标题包含数字和利益词，吸引力较好",
    },
    "emotion_analysis": {
        "positive_ratio": 0.72,
        "empathy_words": ["宝藏", "绝了", "后悔没早看到"],
        "anxiety_words": [],
        "style": "种草",
        "score": 78,
        "comment": "情绪正向积极，种草风格明显",
    },
    "structure_analysis": {
        "selling_points": ["小众打卡地", "性价比高", "交通便利"],
        "point_count": 3,
        "has_pain_point": True,
        "redundancy_notes": ["第二段与第三段内容有重复"],
        "score": 72,
        "comment": "卖点清晰但排序可优化",
    },
    "audience_analysis": {
        "age_range": "20-35",
        "consumption_level": "中等",
        "region": "一线城市",
        "match_score": 80,
        "comment": "目标人群定位准确",
    },
    "overall_scoring": {
        "title_score": 85,
        "emotion_score": 78,
        "structure_score": 72,
        "audience_score": 80,
        "overall_score": 79,
        "overall_grade": "B",
    },
    "suggestions": [
        {
            "type": "title",
            "content": "建议在标题中加入疑问句或反问句式，提升点击率",
            "position": {"start": 0, "end": 20},
        },
        {
            "type": "emotion",
            "content": "中间段落可增加1-2个情绪共鸣点，如使用感叹句式",
            "position": {"start": 80, "end": 160},
        },
        {
            "type": "structure",
            "content": "按「痛点→解决方案→差异化」重新组织卖点顺序",
            "position": {"start": 40, "end": 120},
        },
    ],
}


# 全局单例
_router: LLMRouter | None = None


def get_router() -> LLMRouter:
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router
