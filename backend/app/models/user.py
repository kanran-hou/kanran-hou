"""用户分层模型"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_openid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    tier: Mapped[str] = mapped_column(
        Enum("normal", "frequent", "vip", name="user_tier_enum"),
        nullable=False,
        default="normal",
    )
    daily_analysis_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_analysis_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
