"""5 维度 Pydantic 输出模型 + 聚合 AnalysisResult"""

from __future__ import annotations

from pydantic import BaseModel, Field


class TitleAnalysis(BaseModel):
    """标题分析"""
    has_number: bool = False
    has_question: bool = False
    has_benefit_words: bool = False
    has_emotion_hook: bool = False
    score: int = Field(default=0, ge=0, le=100)
    comment: str = ""


class EmotionAnalysis(BaseModel):
    """情绪分析"""
    positive_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    empathy_words: list[str] = Field(default_factory=list)
    anxiety_words: list[str] = Field(default_factory=list)
    style: str = ""
    score: int = Field(default=0, ge=0, le=100)
    comment: str = ""


class StructureAnalysis(BaseModel):
    """结构分析"""
    selling_points: list[str] = Field(default_factory=list)
    point_count: int = 0
    has_pain_point: bool = False
    redundancy_notes: list[str] = Field(default_factory=list)
    score: int = Field(default=0, ge=0, le=100)
    comment: str = ""


class AudienceAnalysis(BaseModel):
    """人群匹配分析"""
    age_range: str = ""
    consumption_level: str = ""
    region: str = ""
    match_score: int = Field(default=0, ge=0, le=100)
    comment: str = ""


class OverallScoring(BaseModel):
    """综合评分"""
    title_score: int = Field(default=0, ge=0, le=100)
    emotion_score: int = Field(default=0, ge=0, le=100)
    structure_score: int = Field(default=0, ge=0, le=100)
    audience_score: int = Field(default=0, ge=0, le=100)
    overall_score: int = Field(default=0, ge=0, le=100)
    overall_grade: str = "C"


class SuggestionItem(BaseModel):
    """单条优化建议"""
    type: str = ""
    content: str = ""
    position: dict[str, int] = Field(default_factory=lambda: {"start": 0, "end": 0})


class AnalysisResult(BaseModel):
    """聚合分析结果 — 包含 5 维度 + 建议"""
    title_analysis: TitleAnalysis = Field(default_factory=TitleAnalysis)
    emotion_analysis: EmotionAnalysis = Field(default_factory=EmotionAnalysis)
    structure_analysis: StructureAnalysis = Field(default_factory=StructureAnalysis)
    audience_analysis: AudienceAnalysis = Field(default_factory=AudienceAnalysis)
    overall_scoring: OverallScoring = Field(default_factory=OverallScoring)
    suggestions: list[SuggestionItem] = Field(default_factory=list)
