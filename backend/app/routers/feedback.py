"""用户反馈 API 路由"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.feedback import UserFeedback
from app.models.behavior import UsersBehaviorLog
from app.schemas.common import ApiResponse

router = APIRouter(tags=["feedback"])


# ---- Schemas ----

class FeedbackCreate(BaseModel):
    user_openid: str = Field(..., max_length=64, description="用户标识")
    analysis_id: int | None = Field(None, description="关联分析记录 ID")
    feedback_type: str = Field(..., pattern=r"^(analysis_inaccurate|suggestion_invalid|other)$")
    feedback_text: str | None = Field(None, max_length=500, description="反馈内容")


class FeedbackItem(BaseModel):
    id: int
    user_openid: str
    analysis_id: int | None
    feedback_type: str
    feedback_text: str | None
    is_processed: bool = False
    created_at: str


class FeedbackListResponse(BaseModel):
    items: list[FeedbackItem]
    total: int
    page: int
    page_size: int


class ProcessedUpdate(BaseModel):
    is_processed: bool = True


# ---- 用户提交反馈 ----

@router.post("/api/v1/feedback", response_model=ApiResponse)
async def submit_feedback(
    req: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """用户提交反馈"""
    if req.feedback_text and len(req.feedback_text) > 500:
        raise HTTPException(status_code=400, detail="反馈内容不能超过 500 字")

    record = UserFeedback(
        user_openid=req.user_openid,
        analysis_id=req.analysis_id,
        feedback_type=req.feedback_type,
        feedback_text=req.feedback_text,
    )
    db.add(record)
    await db.flush()

    # 行为埋点
    behavior = UsersBehaviorLog(
        user_openid=req.user_openid,
        action_type="feedback",
        action_detail={"feedback_type": req.feedback_type, "feedback_id": record.id},
        analysis_id=req.analysis_id,
    )
    db.add(behavior)

    logger.info("Feedback submitted: user={user}, type={type}", user=req.user_openid, type=req.feedback_type)
    return ApiResponse(code=0, message="感谢您的反馈，我们将持续优化", data={"id": record.id})


# ---- 管理后台接口 ----

@router.get("/api/v1/admin/feedback", response_model=ApiResponse[FeedbackListResponse])
async def list_feedback(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    feedback_type: str | None = Query(None),
    is_processed: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FeedbackListResponse]:
    """管理后台：分页查询反馈列表"""
    query = select(UserFeedback)

    if feedback_type:
        query = query.where(UserFeedback.feedback_type == feedback_type)

    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # 分页
    query = (
        query.order_by(UserFeedback.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    rows = result.scalars().all()

    items = [
        FeedbackItem(
            id=r.id,
            user_openid=r.user_openid,
            analysis_id=r.analysis_id,
            feedback_type=r.feedback_type,
            feedback_text=r.feedback_text,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in rows
    ]

    return ApiResponse(data=FeedbackListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    ))


@router.patch("/api/v1/admin/feedback/{feedback_id}/processed")
async def mark_feedback_processed(
    feedback_id: int,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """管理后台：标记反馈为已处理"""
    row = await db.get(UserFeedback, feedback_id)
    if not row:
        raise HTTPException(status_code=404, detail="反馈记录不存在")

    row.processed = True
    return ApiResponse(message="已标记为已处理")


@router.delete("/api/v1/admin/feedback/{feedback_id}")
async def delete_feedback(
    feedback_id: int,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """管理后台：删除反馈"""
    row = await db.get(UserFeedback, feedback_id)
    if not row:
        raise HTTPException(status_code=404, detail="反馈记录不存在")

    await db.delete(row)
    return ApiResponse(message="已删除")
