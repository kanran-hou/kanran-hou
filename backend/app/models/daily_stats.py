"""每日运营统计模型"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Integer, String, func
from sqlalchemy.dialects.mysql import DECIMAL, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DailyStats(Base):
    __tablename__ = "daily_stats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    stat_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    total_analysis: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_overall_score: Mapped[float | None] = mapped_column(DECIMAL(5, 2), nullable=True)
    grade_distribution: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    track_distribution: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    active_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
