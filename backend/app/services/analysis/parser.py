"""JSON 响应校验模块 — 解析 LLM 输出 → Pydantic 模型"""

from __future__ import annotations

import json
import re

from loguru import logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from app.services.analysis.models import AnalysisResult


class JSONParseError(ValueError):
    """JSON 解析失败"""


class AnalysisParser:
    """解析 LLM 返回的 JSON 字符串 → AnalysisResult"""

    @staticmethod
    def extract_json(text: str) -> str:
        """从 LLM 回复中提取 JSON 部分（处理 markdown 包裹等情况）"""
        # 尝试提取 ```json ... ``` 包裹
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if match:
            return match.group(1).strip()
        # 尝试提取最外层 { ... }
        brace_match = re.search(r"\{[\s\S]*\}", text)
        if brace_match:
            return brace_match.group(0)
        return text.strip()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(JSONParseError),
    )
    async def parse(self, raw_text: str) -> AnalysisResult:
        """解析 JSON → AnalysisResult，失败自动重试"""
        try:
            cleaned = self.extract_json(raw_text)
            data = json.loads(cleaned)
            return AnalysisResult.model_validate(data)
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning("JSON parse failed: {e}, raw={raw}", e=e, raw=raw_text[:200])
            raise JSONParseError(f"JSON parse failed: {e}") from e

    @staticmethod
    def safe_parse(raw_text: str) -> AnalysisResult | None:
        """单次安全解析，不重试，失败返回 None"""
        try:
            cleaned = AnalysisParser.extract_json(raw_text)
            data = json.loads(cleaned)
            return AnalysisResult.model_validate(data)
        except Exception:
            return None
