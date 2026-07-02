"""文案分析 API 端点 — POST /api/v1/analyze"""

from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from loguru import logger
from app.config import settings
from app.models import CopywritingAnalysis, UsersBehaviorLog, User
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.schemas.common import ApiResponse
from app.services.analysis.models import AnalysisResult
from app.services.analysis.parser import AnalysisParser
from app.services.analysis.scorer import ScoreCalculator
from app.services.llm.router import get_router, AllProvidersFailedError
from app.services.prompts.manager import get_prompt_manager, PromptNotFoundError
from app.services.suggestions.generator import SuggestionGenerator
from app.services.suggestions.models import OptimizationSuggestion
from app.utils.string_utils import count_chars

router = APIRouter(prefix="/api/v1", tags=["analysis"])
parser = AnalysisParser()

VALID_TRACKS = {"xiaohongshu", "ecommerce", "local_tourism", "short_video"}
MAX_TEXT_LENGTH = 5000


def _validate_request(req: AnalysisRequest) -> None:
    stripped = req.original_text.strip()
    if not stripped:
        raise HTTPException(status_code=400, detail="文案内容不能为空")
    if count_chars(stripped) > MAX_TEXT_LENGTH:
        raise HTTPException(status_code=413, detail=f"文案长度超过 {MAX_TEXT_LENGTH} 字限制")
    if req.track_type not in VALID_TRACKS:
        raise HTTPException(status_code=400, detail="无效赛道参数")


async def _try_save_to_db(db, user_openid, text, track, result, word_count):
    try:
        record = CopywritingAnalysis(
            user_openid=user_openid, original_text=text, track_type=track,
            title_score=result.overall_scoring.title_score,
            emotion_score=result.overall_scoring.emotion_score,
            structure_score=result.overall_scoring.structure_score,
            audience_score=result.overall_scoring.audience_score,
            overall_score=result.overall_scoring.overall_score,
            overall_grade=result.overall_scoring.overall_grade,
            analysis_raw=result.model_dump(), word_count=word_count,
        )
        db.add(record)
        await db.flush()
        behavior = UsersBehaviorLog(
            user_openid=user_openid, action_type="analyze",
            action_detail={"track_type": track, "word_count": word_count},
            analysis_id=record.id
        )
        db.add(behavior)
        return record.id
    except Exception as e:
        await db.rollback()
        logger.warning("DB save skipped (dev mode): {e}", e=e)
        return 0


@router.post("/analyze", response_model=ApiResponse[AnalysisResponse])
async def analyze_copywriting(
    req: AnalysisRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AnalysisResponse]:
    _validate_request(req)
    text = req.original_text.strip()
    track = req.track_type
    user_openid = req.user_openid or "anonymous"

    # 1) 获取 Prompt 模板
    try:
        prompt_mgr = get_prompt_manager()
        prompt = prompt_mgr.get(track)
    except PromptNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2) 调用 DeepSeek LLM
    messages = prompt.build_messages(text)
    llm_router = get_router()
    try:
        raw_response = await llm_router.chat(messages)
    except AllProvidersFailedError as e:
        logger.error("All LLM providers failed: {e}", e=e)
        raise HTTPException(status_code=503, detail="AI 服务暂不可用")

    # 3) 解析 LLM JSON 输出
    try:
        result = await parser.parse(raw_response)
    except Exception as e:
        logger.warning("Parse failed, fallback: {e}", e=e)
        result = _fallback_analysis(text, track)

    # 4) 补充评分与规则建议
    if result.overall_scoring.overall_score == 0:
        overall = ScoreCalculator.calculate(
            title_score=result.title_analysis.score,
            emotion_score=result.emotion_analysis.score,
            structure_score=result.structure_analysis.score,
            audience_score=result.audience_analysis.score, weights=prompt.weights,
        )
        result.overall_scoring = overall
    for s in SuggestionGenerator.generate(result):
        if s.type not in {x.type for x in result.suggestions}:
            result.suggestions.append(
                OptimizationSuggestion(type=s.type, content=s.content, position=s.position)
            )

    # 5) 保存到数据库（可选，无 MySQL 时自动跳过）
    word_count = count_chars(text)
    analysis_id = await _try_save_to_db(db, user_openid, text, track, result, word_count)

    # 6) 返回结果
    resp = AnalysisResponse(
        id=analysis_id,
        title_score=result.overall_scoring.title_score,
        emotion_score=result.overall_scoring.emotion_score,
        structure_score=result.overall_scoring.structure_score,
        audience_score=result.overall_scoring.audience_score,
        overall_score=result.overall_scoring.overall_score,
        overall_grade=result.overall_scoring.overall_grade,
        word_count=word_count,
        analysis_raw=result.model_dump(),
        created_at=datetime.now(timezone.utc),
    )
    return ApiResponse(code=0, message="success", data=resp)


def _fallback_analysis(text, track):
    wc = count_chars(text)
    sb = min(70, 30 + wc // 10)
    return AnalysisResult(
        title_analysis={"score": 50, "comment": "标题分析暂不可用"},
        emotion_analysis={"score": 50, "comment": "情绪分析暂不可用"},
        structure_analysis={"score": sb, "comment": "基于规则的预估"},
        audience_analysis={"score": 50, "comment": "人群分析暂不可用"},
        overall_scoring={"overall_score": 50, "overall_grade": "B"},
    )