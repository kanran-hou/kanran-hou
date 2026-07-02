"""评分计算器 — 加权总分 → S/A/B/C 评级映射"""

from __future__ import annotations

from app.services.analysis.models import OverallScoring


def compute_grade(overall_score: int) -> str:
    """根据综合分映射评级"""
    if overall_score >= 85:
        return "S"
    elif overall_score >= 70:
        return "A"
    elif overall_score >= 50:
        return "B"
    else:
        return "C"


class ScoreCalculator:
    """评分计算器：加权计算总分 + 评级"""

    WEIGHT_MAP: dict[str, float] = {
        "title": 0.25,
        "emotion": 0.25,
        "structure": 0.25,
        "audience": 0.25,
    }

    @classmethod
    def calculate(
        cls,
        title_score: int,
        emotion_score: int,
        structure_score: int,
        audience_score: int,
        weights: dict[str, float] | None = None,
    ) -> OverallScoring:
        """计算综合评分与评级"""
        w = weights or cls.WEIGHT_MAP
        overall = round(
            title_score * w.get("title", 0.25)
            + emotion_score * w.get("emotion", 0.25)
            + structure_score * w.get("structure", 0.25)
            + audience_score * w.get("audience", 0.25)
        )
        overall = max(0, min(100, overall))
        grade = compute_grade(overall)

        return OverallScoring(
            title_score=title_score,
            emotion_score=emotion_score,
            structure_score=structure_score,
            audience_score=audience_score,
            overall_score=overall,
            overall_grade=grade,
        )
