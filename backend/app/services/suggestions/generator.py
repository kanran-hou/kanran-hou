"""建议生成模块 — 基于 5 维度得分定位缺陷 → 生成对应建议"""

from __future__ import annotations

from app.services.analysis.models import AnalysisResult
from app.services.suggestions.models import OptimizationSuggestion


class SuggestionGenerator:
    """基于分数阈值的规则式建议生成器"""

    THRESHOLDS = {
        "title": {"low": 70, "mid": 85},
        "emotion": {"low": 65, "mid": 80},
        "structure": {"low": 65, "mid": 80},
        "audience": {"low": 60, "mid": 75},
    }

    @classmethod
    def generate(cls, result: AnalysisResult) -> list[OptimizationSuggestion]:
        """基于分析结果生成优化建议"""
        suggestions: list[OptimizationSuggestion] = []

        # 标题建议
        title = result.title_analysis
        if title.score < cls.THRESHOLDS["title"]["low"]:
            suggestions.append(OptimizationSuggestion(
                type="title",
                content="标题吸引力不足，建议加入数字、疑问句或情绪钩子（如「绝了」「必看」）提升点击率",
                position={"start": 0, "end": max(len(result.title_analysis.comment), 20)},
            ))
        elif title.score < cls.THRESHOLDS["title"]["mid"]:
            if not title.has_number:
                suggestions.append(OptimizationSuggestion(
                    type="title",
                    content="标题可加入数字（如「3个技巧」「5分钟搞定」）增强具体感和可信度",
                    position={"start": 0, "end": 20},
                ))
            if not title.has_emotion_hook:
                suggestions.append(OptimizationSuggestion(
                    type="title",
                    content="标题缺少情绪钩子，尝试加入感叹句式或引发好奇心的表达",
                    position={"start": 0, "end": 20},
                ))

        # 情绪建议
        emotion = result.emotion_analysis
        if emotion.score < cls.THRESHOLDS["emotion"]["low"]:
            suggestions.append(OptimizationSuggestion(
                type="emotion",
                content="情绪表达较平淡，建议加入共鸣话术（如「谁懂啊」「只有我这样吗」）和情感波动点",
                position={"start": 0, "end": 80},
            ))
        elif emotion.score < cls.THRESHOLDS["emotion"]["mid"]:
            if emotion.positive_ratio < 0.5:
                suggestions.append(OptimizationSuggestion(
                    type="emotion",
                    content="正向情绪占比较低，建议增加积极情感表达和用户受益描述",
                    position={"start": 0, "end": 80},
                ))
            if not emotion.empathy_words:
                suggestions.append(OptimizationSuggestion(
                    type="emotion",
                    content="缺少共情词，加入「姐妹们」「打工人」「学生党」等身份认同话术增强代入感",
                    position={"start": 0, "end": 80},
                ))

        # 结构建议
        structure = result.structure_analysis
        if structure.score < cls.THRESHOLDS["structure"]["low"]:
            suggestions.append(OptimizationSuggestion(
                type="structure",
                content="卖点结构不清晰，建议重新按「痛点→解决方案→差异化优势」组织内容",
                position={"start": 0, "end": 120},
            ))
        elif structure.score < cls.THRESHOLDS["structure"]["mid"]:
            if structure.point_count < 2:
                suggestions.append(OptimizationSuggestion(
                    type="structure",
                    content="卖点数量不足（仅 {count} 个），建议挖掘至少 3 个差异化卖点",
                    position={"start": 0, "end": 120},
                ))
            if not structure.has_pain_point:
                suggestions.append(OptimizationSuggestion(
                    type="structure",
                    content="缺少对用户痛点的描述，开门见山指出用户遇到的问题能有效提升转化",
                    position={"start": 0, "end": 120},
                ))

        return suggestions
