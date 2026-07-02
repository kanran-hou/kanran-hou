"""数据库模型测试"""

from __future__ import annotations

import pytest
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CopywritingAnalysis, UsersBehaviorLog, UserFeedback


@pytest.mark.asyncio
async def test_create_analysis(db_session: AsyncSession) -> None:
   """验证 CopywritingAnalysis 模型的创建和字段"""
   analysis = CopywritingAnalysis(
       user_openid="test_user",
       original_text="测试文案内容",
       track_type="xiaohongshu",
       title_score=85.0,
       emotion_score=78.0,
       structure_score=72.0,
       audience_score=80.0,
       overall_score=79.0,
       overall_grade="B",
       analysis_raw={"keywords": ["测试"]},
       word_count=5,
   )
   db_session.add(analysis)
   await db_session.flush()

   assert analysis.id is not None
   assert analysis.user_openid == "test_user"
   assert analysis.track_type == "xiaohongshu"
   assert analysis.overall_grade == "B"


@pytest.mark.asyncio
async def test_behavior_log(db_session: AsyncSession) -> None:
   """验证 UsersBehaviorLog 模型"""
   log = UsersBehaviorLog(
       user_openid="test_user",
       action_type="analyze",
       action_detail={"source": "manual"},
   )
   db_session.add(log)
   await db_session.flush()

   assert log.id is not None
   assert log.action_type == "analyze"


@pytest.mark.asyncio
async def test_user_feedback(db_session: AsyncSession) -> None:
   """验证 UserFeedback 模型"""
   feedback = UserFeedback(
       user_openid="test_user",
       feedback_type="inaccurate",
       feedback_text="评分不太准确",
   )
   db_session.add(feedback)
   await db_session.flush()

   assert feedback.id is not None
   assert feedback.feedback_type == "inaccurate"


@pytest.mark.asyncio
async def test_model_relationships(db_session: AsyncSession) -> None:
   """验证模型间外键关系"""
   analysis = CopywritingAnalysis(
       user_openid="test_user",
       original_text="关系测试文案",
       track_type="ecommerce",
   )
   db_session.add(analysis)
   await db_session.flush()

   log = UsersBehaviorLog(
       user_openid="test_user",
       action_type="export",
       analysis_id=analysis.id,
   )
   db_session.add(log)
   await db_session.flush()

   feedback = UserFeedback(
       user_openid="test_user",
       analysis_id=analysis.id,
       feedback_type="other",
       feedback_text="关系测试",
   )
   db_session.add(feedback)
   await db_session.flush()

   assert log.analysis_id == analysis.id
   assert feedback.analysis_id == analysis.id
