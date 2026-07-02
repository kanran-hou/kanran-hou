"""CopyMind 历史记录 API 路由"""

from __future__ import annotations

import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.copywriting import CopywritingAnalysis

router = APIRouter(prefix="/api/v1/history", tags=["history"])


@router.get("")
async def list_history(
    user_openid: str = Query("", description="用户标识"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """分页查询历史记录"""
    query = select(CopywritingAnalysis)

    if user_openid:
        query = query.where(CopywritingAnalysis.user_openid == user_openid)

    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # 分页
    query = (
        query.order_by(CopywritingAnalysis.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    rows = result.scalars().all()

    items = []
    for row in rows:
        items.append({
            "id": row.id,
            "track_type": row.track_type,
            "track_name": row.track_name or "",
            "text_preview": (row.raw_text or "")[:50],
            "overall_score": row.overall_score,
            "overall_grade": row.overall_grade,
            "created_at": row.created_at.isoformat() if row.created_at else "",
        })

    return {
        "code": 0,
        "message": "ok",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


@router.get("/{analysis_id}")
async def get_history_detail(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """获取单条历史记录详情"""
    row = await db.get(CopywritingAnalysis, analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail="记录不存在")

    return {
        "code": 0,
        "message": "ok",
        "data": {
            "id": row.id,
            "track_type": row.track_type,
            "track_name": row.track_name or "",
            "raw_text": row.raw_text,
            "overall_score": row.overall_score,
            "overall_grade": row.overall_grade,
            "percentile": row.percentile,
            "dimensions": row.dimensions or [],
            "emotion_words": row.emotion_words or {},
            "suggestions": row.suggestions or {},
            "reference_cases": row.reference_cases or [],
            "created_at": row.created_at.isoformat() if row.created_at else "",
        },
    }


@router.delete("/{analysis_id}")
async def delete_history(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """删除历史记录"""
    row = await db.get(CopywritingAnalysis, analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail="记录不存在")

    await db.delete(row)
    await db.commit()
    return {"code": 0, "message": "已删除", "data": None}
