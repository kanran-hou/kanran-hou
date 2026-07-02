"""CopyMind 定时任务模块 — APScheduler"""

from __future__ import annotations

import asyncio
from datetime import date, timedelta

from loguru import logger
from sqlalchemy import select, func

from app.database import async_session_factory
from app.models import CopywritingAnalysis, DailyStats


async def compute_daily_stats(target_date: date | None = None) -> dict:
    """计算并存储指定日期的运营指标"""
    if target_date is None:
        target_date = date.today() - timedelta(days=1)

    async with async_session_factory() as db:
        try:
            # 总分析次数
            q_count = select(func.count()).where(
                func.date(CopywritingAnalysis.created_at) == target_date
            )
            r = await db.execute(q_count)
            total_analysis = r.scalar() or 0

            # 平均分
            q_avg = select(func.avg(CopywritingAnalysis.overall_score)).where(
                func.date(CopywritingAnalysis.created_at) == target_date
            )
            r = await db.execute(q_avg)
            avg_score = float(r.scalar() or 0)

            # 评级分布
            grade_dist = {}
            for g in ["S", "A", "B", "C"]:
                qg = select(func.count()).where(
                    func.date(CopywritingAnalysis.created_at) == target_date,
                    CopywritingAnalysis.overall_grade == g,
                )
                rg = await db.execute(qg)
                grade_dist[g] = rg.scalar() or 0

            # 赛道分布
            track_dist = {}
            for t in ["xiaohongshu", "ecommerce", "local_tourism", "short_video"]:
                qt = select(func.count()).where(
                    func.date(CopywritingAnalysis.created_at) == target_date,
                    CopywritingAnalysis.track_type == t,
                )
                rt = await db.execute(qt)
                track_dist[t] = rt.scalar() or 0

            # 活跃用户数
            q_au = select(func.count(func.distinct(CopywritingAnalysis.user_openid))).where(
                func.date(CopywritingAnalysis.created_at) == target_date
            )
            r_au = await db.execute(q_au)
            active_users = r_au.scalar() or 0

            # Upsert daily_stats
            q_exist = select(DailyStats).where(DailyStats.stat_date == target_date)
            r_exist = await db.execute(q_exist)
            existing = r_exist.scalar_one_or_none()

            if existing:
                existing.total_analysis = total_analysis
                existing.avg_overall_score = round(avg_score, 2)
                existing.grade_distribution = grade_dist
                existing.track_distribution = track_dist
                existing.active_users = active_users
            else:
                stats = DailyStats(
                    stat_date=target_date,
                    total_analysis=total_analysis,
                    avg_overall_score=round(avg_score, 2),
                    grade_distribution=grade_dist,
                    track_distribution=track_dist,
                    active_users=active_users,
                )
                db.add(stats)

            await db.commit()
            logger.info("Daily stats computed for {date}: {total} analyses", date=target_date, total=total_analysis)

            return {
                "date": target_date.isoformat(),
                "total_analysis": total_analysis,
                "avg_overall_score": round(avg_score, 2),
                "grade_distribution": grade_dist,
                "track_distribution": track_dist,
                "active_users": active_users,
            }

        except Exception as e:
            await db.rollback()
            logger.error("Failed to compute daily stats: {e}", e=e)
            raise


def run_daily_stats_sync():
    """同步入口（供 APScheduler 调用）"""
    target = date.today() - timedelta(days=1)
    asyncio.run(compute_daily_stats(target))
