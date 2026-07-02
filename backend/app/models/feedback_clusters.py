"""反馈聚类结果模型"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FeedbackCluster(Base):
    __tablename__ = "feedback_clusters"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cluster_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cluster_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sample_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sample_texts: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_week: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
