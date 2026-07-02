"""知识库相关 Pydantic schemas"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """知识库搜索请求"""
    query: str = Field(..., min_length=1, max_length=5000, description="搜索文本")
    track_type: str | None = Field(None, description="赛道过滤，为空则搜索全部")
    top_k: int = Field(5, ge=1, le=20, description="返回条数")


class TemplateMatch(BaseModel):
    """模板匹配结果"""
    rank: int = 0
    score: float = 0.0
    track_type: str = ""
    title: str = ""
    content: str = ""
    tags: list[str] = Field(default_factory=list)
    overall_score: int = 0
    source: str = ""


class SearchResponse(BaseModel):
    """搜索响应"""
    templates: list[TemplateMatch] = Field(default_factory=list)
    total: int = 0
    query_track: str | None = None


class ReferenceCase(BaseModel):
    """注入到分析结果中的参考案例"""
    title: str = ""
    score: int = 0
    tags: list[str] = Field(default_factory=list)
    similarity: float = 0.0