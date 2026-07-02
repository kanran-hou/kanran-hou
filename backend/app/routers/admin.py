"""运营管理后台 API 路由"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import settings
from app.models import CopywritingAnalysis, UsersBehaviorLog, User, DailyStats, FeedbackCluster
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# ---- Schemas ----

class DashboardStats(BaseModel):
    """数据看板核心指标"""
    total_analysis_today: int = 0
    total_analysis_week: int = 0
    total_analysis_month: int = 0
    total_analysis_all: int = 0
    avg_overall_score: float = 0
    grade_distribution: dict = {}
    track_distribution: dict = {}
    active_users_daily: int = 0
    active_users_weekly: int = 0
    active_users_monthly: int = 0


class TrendItem(BaseModel):
    date: str
    count: int


class DefectItem(BaseModel):
    dimension: str
    name: str
    low_score_count: int
    percentage: float


class UserBatchGrant(BaseModel):
    user_openids: list[str] = Field(..., min_length=1, max_length=50)
    tier: str = Field("frequent", pattern=r"^(frequent|vip)$")


class BatchAnalysisRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=5, description="文案列表")
    track_type: str = Field(..., pattern=r"^(xiaohongshu|ecommerce|local_tourism|short_video)$")


# ---- 6.3 数据看板 ----

@router.get("/dashboard", response_model=ApiResponse[DashboardStats])
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DashboardStats]:
    """获取数据看板核心指标"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    async def _count_since(since_date: date | None = None) -> int:
        q = select(func.count()).select_from(CopywritingAnalysis)
        if since_date:
            q = q.where(CopywritingAnalysis.created_at >= since_date)
        r = await db.execute(q)
        return r.scalar() or 0

    total_all = await _count_since()
    total_today = await _count_since(today)
    total_week = await _count_since(week_start)
    total_month = await _count_since(month_start)

    # 平均分
    avg_q = select(func.avg(CopywritingAnalysis.overall_score))
    avg_r = await db.execute(avg_q)
    avg_score = float(avg_r.scalar() or 0)

    # 各评级分布
    grade_counts = {}
    for g in ["S", "A", "B", "C"]:
        gq = select(func.count()).where(CopywritingAnalysis.overall_grade == g)
        gr = await db.execute(gq)
        grade_counts[g] = gr.scalar() or 0

    # 各赛道分布
    track_counts = {}
    for t in ["xiaohongshu", "ecommerce", "local_tourism", "short_video"]:
        tq = select(func.count()).where(CopywritingAnalysis.track_type == t)
        tr = await db.execute(tq)
        track_counts[t] = tr.scalar() or 0

    # 活跃用户数
    async def _active_users(since: date | None = None) -> int:
        q = select(func.count(func.distinct(CopywritingAnalysis.user_openid)))
        if since:
            q = q.where(CopywritingAnalysis.created_at >= since)
        r = await db.execute(q)
        return r.scalar() or 0

    au_daily = await _active_users(today)
    au_weekly = await _active_users(week_start)
    au_monthly = await _active_users(month_start)

    return ApiResponse(data=DashboardStats(
        total_analysis_today=total_today,
        total_analysis_week=total_week,
        total_analysis_month=total_month,
        total_analysis_all=total_all,
        avg_overall_score=round(avg_score, 2),
        grade_distribution=grade_counts,
        track_distribution=track_counts,
        active_users_daily=au_daily,
        active_users_weekly=au_weekly,
        active_users_monthly=au_monthly,
    ))


@router.get("/dashboard/trend", response_model=ApiResponse[list[TrendItem]])
async def get_analysis_trend(
    days: int = Query(7, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[TrendItem]]:
    """获取分析量趋势"""
    since = date.today() - timedelta(days=days - 1)

    # Try daily_stats table first
    stat_q = select(DailyStats).where(DailyStats.stat_date >= since).order_by(DailyStats.stat_date)
    stat_r = await db.execute(stat_q)
    stats_map = {s.stat_date: s.total_analysis for s in stat_r.scalars().all()}

    items = []
    for i in range(days):
        d = since + timedelta(days=i)
        count = stats_map.get(d, 0)
        if count == 0:
            # Fallback: count from analysis table
            q = select(func.count()).where(
                func.date(CopywritingAnalysis.created_at) == d
            )
            r = await db.execute(q)
            count = r.scalar() or 0
        items.append(TrendItem(date=d.isoformat(), count=count))

    return ApiResponse(data=items)


@router.get("/dashboard/defects", response_model=ApiResponse[list[DefectItem]])
async def get_defect_ranking(
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[DefectItem]]:
    """获取高频缺陷类型排行榜"""
    dims = [
        ("title_score", "标题吸引力", 60),
        ("emotion_score", "情绪感染力", 60),
        ("structure_score", "卖点结构", 60),
        ("audience_score", "人群匹配", 60),
    ]

    total_q = select(func.count()).select_from(CopywritingAnalysis)
    total_r = await db.execute(total_q)
    total = total_r.scalar() or 1

    items = []
    for col, name, threshold in dims:
        col_attr = getattr(CopywritingAnalysis, col)
        q = select(func.count()).where(col_attr < threshold)
        r = await db.execute(q)
        count = r.scalar() or 0
        items.append(DefectItem(
            dimension=col,
            name=name,
            low_score_count=count,
            percentage=round(count / total * 100, 1),
        ))

    items.sort(key=lambda x: x.low_score_count, reverse=True)
    return ApiResponse(data=items)


@router.get("/dashboard/behavior", response_model=ApiResponse[dict])
async def get_behavior_stats(
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    """获取功能点击率统计"""
    q = select(
        UsersBehaviorLog.action_type,
        func.count().label("count"),
    ).group_by(UsersBehaviorLog.action_type).order_by(func.count().desc())
    r = await db.execute(q)
    data = {row.action_type: row.count for row in r}
    return ApiResponse(data=data)


# ---- 6.2 用户分层 ----

@router.post("/users/batch", response_model=ApiResponse)
async def batch_grant_user(
    req: UserBatchGrant,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """批量开通高频/VIP 权限（管理员接口）"""
    granted = 0
    for openid in req.user_openids:
        # Upsert
        q = select(User).where(User.user_openid == openid)
        r = await db.execute(q)
        user = r.scalar_one_or_none()
        if user:
            user.tier = req.tier
        else:
            user = User(user_openid=openid, tier=req.tier)
            db.add(user)
        granted += 1

    logger.info("Batch grant: {count} users -> {tier}", count=granted, tier=req.tier)
    return ApiResponse(message=f"已为 {granted} 名用户开通 {req.tier} 权限")


@router.get("/users/stats", response_model=ApiResponse[dict])
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    """获取用户分层统计数据"""
    tiers = ["normal", "frequent", "vip"]
    result = {}
    for t in tiers:
        q = select(func.count()).where(User.tier == t)
        r = await db.execute(q)
        result[t] = r.scalar() or 0
    result["total"] = sum(result.values())
    return ApiResponse(data=result)


# ---- 聚类报告 ----

@router.get("/clusters", response_model=ApiResponse[list[dict]])
async def get_feedback_clusters(
    week: str | None = Query(None, description="统计周，如 2026-W27"),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[dict]]:
    """获取反馈聚类报告"""
    q = select(FeedbackCluster)
    if week:
        q = q.where(FeedbackCluster.created_week == week)
    q = q.order_by(FeedbackCluster.created_week.desc(), FeedbackCluster.cluster_id)
    r = await db.execute(q)
    rows = r.scalars().all()
    items = []
    for row in rows:
        items.append({
            "id": row.id,
            "cluster_id": row.cluster_id,
            "cluster_label": row.cluster_label,
            "sample_count": row.sample_count,
            "sample_texts": row.sample_texts,
            "created_week": row.created_week,
        })
    return ApiResponse(data=items)
