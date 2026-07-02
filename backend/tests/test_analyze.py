"""Phase 2 — AI 分析模块测试"""

from __future__ import annotations

import json

import pytest
from httpx import AsyncClient

from app.services.analysis.parser import AnalysisParser
from app.services.analysis.scorer import ScoreCalculator, compute_grade
from app.services.analysis.models import (
   AnalysisResult, TitleAnalysis, EmotionAnalysis,
   StructureAnalysis, AudienceAnalysis, OverallScoring,
)
from app.services.suggestions.generator import SuggestionGenerator
from app.services.prompts.manager import PromptManager, PromptNotFoundError


# ===== 评分计算器测试 =====

class TestScoreCalculator:
   def test_compute_grade_s(self):
       assert compute_grade(85) == "S"
       assert compute_grade(100) == "S"

   def test_compute_grade_a(self):
       assert compute_grade(70) == "A"
       assert compute_grade(84) == "A"

   def test_compute_grade_b(self):
       assert compute_grade(50) == "B"
       assert compute_grade(69) == "B"

   def test_compute_grade_c(self):
       assert compute_grade(0) == "C"
       assert compute_grade(49) == "C"

   def test_calculate_default_weights(self):
       result = ScoreCalculator.calculate(
           title_score=90, emotion_score=80,
           structure_score=70, audience_score=60,
       )
       assert result.overall_score == 75  # (90+80+70+60)/4
       assert result.overall_grade == "A"

   def test_calculate_custom_weights(self):
       w = {"title": 0.4, "emotion": 0.2, "structure": 0.3, "audience": 0.1}
       result = ScoreCalculator.calculate(
           title_score=100, emotion_score=80,
           structure_score=60, audience_score=40,
           weights=w,
       )
       expected = round(100*0.4 + 80*0.2 + 60*0.3 + 40*0.1)
       assert result.overall_score == expected

   def test_calculate_clamp(self):
       result = ScoreCalculator.calculate(
           title_score=-10, emotion_score=50,
           structure_score=50, audience_score=50,
       )
       assert result.overall_score >= 0
       result = ScoreCalculator.calculate(
           title_score=200, emotion_score=50,
           structure_score=50, audience_score=50,
       )
       assert result.overall_score <= 100


# ===== JSON 解析器测试 =====

class TestAnalysisParser:
   SAMPLE_JSON = """
   {
       "title_analysis": {"has_number": true, "has_question": false, "has_benefit_words": true, "has_emotion_hook": false, "score": 85, "comment": "好标题"},
       "emotion_analysis": {"positive_ratio": 0.7, "empathy_words": ["绝了"], "anxiety_words": [], "style": "种草", "score": 78, "comment": ""},
       "structure_analysis": {"selling_points": ["点1"], "point_count": 1, "has_pain_point": true, "redundancy_notes": [], "score": 72, "comment": ""},
       "audience_analysis": {"age_range": "20-30", "consumption_level": "中", "region": "一线", "match_score": 80, "comment": ""},
       "overall_scoring": {"title_score": 85, "emotion_score": 78, "structure_score": 72, "audience_score": 80, "overall_score": 79, "overall_grade": "B"},
       "suggestions": [{"type": "title", "content": "加数字", "position": {"start": 0, "end": 10}}]
   }
   """

   def setup_method(self):
       self.parser = AnalysisParser()

   def test_extract_plain_json(self):
       result = AnalysisParser.extract_json(self.SAMPLE_JSON)
       parsed = json.loads(result)
       assert parsed["title_analysis"]["score"] == 85

   def test_extract_markdown_json(self):
       text = "一些文字```json\n{\"title_analysis\": {\"score\": 90}}\n```"
       result = AnalysisParser.extract_json(text)
       assert json.loads(result)["title_analysis"]["score"] == 90

   @pytest.mark.asyncio
   async def test_parse_valid(self):
       result = await self.parser.parse(self.SAMPLE_JSON)
       assert isinstance(result, AnalysisResult)
       assert result.title_analysis.score == 85
       assert result.overall_scoring.overall_grade == "B"
       assert len(result.suggestions) == 1

   def test_safe_parse_invalid(self):
       result = AnalysisParser.safe_parse("{invalid json}")
       assert result is None


# ===== Prompt 管理器测试 =====

class TestPromptManager:
   def setup_method(self):
       self.mgr = PromptManager()

   def test_get_valid_track(self):
       prompt = self.mgr.get("xiaohongshu")
       assert prompt.track_type == "xiaohongshu"
       assert prompt.version == "1.0"

   def test_get_invalid_track(self):
       with pytest.raises(PromptNotFoundError):
           self.mgr.get("invalid_track")

   def test_list_tracks(self):
       tracks = self.mgr.list_tracks()
       types = {t["track_type"] for t in tracks}
       assert types == {"xiaohongshu", "ecommerce", "local_tourism", "short_video"}

   def test_build_messages(self):
       prompt = self.mgr.get("xiaohongshu")
       msgs = prompt.build_messages("测试文案内容")
       assert len(msgs) == 2
       assert msgs[0]["role"] == "system"
       assert msgs[1]["role"] == "user"
       assert "测试文案内容" in msgs[1]["content"]


# ===== 建议生成器测试 =====

class TestSuggestionGenerator:
   def test_generate_low_title_score(self):
       result = AnalysisResult(
           title_analysis=TitleAnalysis(score=50, has_number=False, has_question=False, has_benefit_words=False, has_emotion_hook=False),
           emotion_analysis=EmotionAnalysis(score=80),
           structure_analysis=StructureAnalysis(score=80, point_count=3, has_pain_point=True),
           audience_analysis=AudienceAnalysis(match_score=80),
           overall_scoring=OverallScoring(overall_score=70, overall_grade="A"),
       )
       suggestions = SuggestionGenerator.generate(result)
       title_sugs = [s for s in suggestions if s.type == "title"]
       assert len(title_sugs) >= 1

   def test_generate_high_scores_no_suggestions(self):
       result = AnalysisResult(
           title_analysis=TitleAnalysis(score=95, has_number=True, has_question=True, has_benefit_words=True, has_emotion_hook=True),
           emotion_analysis=EmotionAnalysis(score=90, positive_ratio=0.9, empathy_words=["绝了", "宝藏"]),
           structure_analysis=StructureAnalysis(score=90, point_count=4, has_pain_point=True),
           audience_analysis=AudienceAnalysis(match_score=90),
           overall_scoring=OverallScoring(overall_score=92, overall_grade="S"),
       )
       suggestions = SuggestionGenerator.generate(result)
       assert len(suggestions) == 0


# ===== API 端点集成测试 =====

class TestAnalyzeEndpoint:
   @pytest.mark.asyncio
   async def test_analyze_empty_text(self, client: AsyncClient):
       resp = await client.post("/api/v1/analyze", json={
           "original_text": "",
           "track_type": "xiaohongshu",
       })
       assert resp.status_code == 400

   @pytest.mark.asyncio
   async def test_analyze_invalid_track(self, client: AsyncClient):
       resp = await client.post("/api/v1/analyze", json={
           "original_text": "测试文案",
           "track_type": "invalid",
       })
       assert resp.status_code == 400

   @pytest.mark.asyncio
   async def test_analyze_too_long(self, client: AsyncClient):
       long_text = "字" * 6000
       resp = await client.post("/api/v1/analyze", json={
           "original_text": long_text,
           "track_type": "xiaohongshu",
       })
       assert resp.status_code == 413

   @pytest.mark.asyncio
   async def test_analyze_valid_request(self, client: AsyncClient):
       """有效请求应返回 200 和结构化响应"""
       resp = await client.post("/api/v1/analyze", json={
           "original_text": "标题：3个你不知道的宝藏旅行地\n\n正文：这些地方真的绝了，姐妹们一定要去！",
           "track_type": "xiaohongshu",
       })
       assert resp.status_code == 200
       data = resp.json()
       assert data["code"] == 0
       assert data["data"]["overall_grade"] is not None

   @pytest.mark.asyncio
   async def test_analyze_all_tracks(self, client: AsyncClient):
       """4 种赛道均能返回结果"""
       for track in ["xiaohongshu", "ecommerce", "local_tourism", "short_video"]:
           resp = await client.post("/api/v1/analyze", json={
               "original_text": f"测试文案——{track}赛道测试内容",
               "track_type": track,
           })
           assert resp.status_code == 200, f"Track {track} failed"
           data = resp.json()
           assert data["data"]["overall_grade"] in ("S", "A", "B", "C")
