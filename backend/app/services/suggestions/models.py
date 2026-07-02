"""优化建议 Pydantic 模型"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PositionRange(BaseModel):
    """原文位置标注：字符偏移范围"""
    start: int = 0
    end: int = 0


class OptimizationSuggestion(BaseModel):
    """优化建议"""
    type: str = ""  # title / emotion / structure
    content: str = ""
    position: PositionRange = Field(default_factory=PositionRange)


class SuggestionResult(BaseModel):
    """聚合优化建议结果"""
    title_suggestions: list[OptimizationSuggestion] = Field(default_factory=list)
    emotion_suggestions: list[OptimizationSuggestion] = Field(default_factory=list)
    structure_suggestions: list[OptimizationSuggestion] = Field(default_factory=list)
