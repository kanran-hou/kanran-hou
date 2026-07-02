"""文案分析相关 Pydantic schemas"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """提交文案分析请求"""

    original_text: str = Field(..., min_length=1, max_length=10000, description="用户原文")
    user_openid: str = Field("anonymous", max_length=64, description="用户标识（可选，用于限流与记录）")
    track_type: str = Field(
        ...,
        pattern=r"^(xiaohongshu|ecommerce|local_tourism|short_video)$",
        description="赛道类型",
    )


class ScoreDetail(BaseModel):
    """单维度评分"""

    score: float = Field(..., ge=0, le=100)
    comment: str = ""


class AnalysisResponse(BaseModel):
    """文案分析结果"""

    id: int
    title_score: float | None = None
    emotion_score: float | None = None
    structure_score: float | None = None
    audience_score: float | None = None
    overall_score: float | None = None
    overall_grade: str | None = None
    word_count: int | None = None
    analysis_raw: dict | None = None
    created_at: datetime | None = None


class AnalysisDetailResponse(AnalysisResponse):
    """包含完整分析详情的响应"""

    original_text: str
    track_type: str
    analysis_raw: dict | None = None
    suggestions: list[str] = Field(default_factory=list, description="优化建议列表")