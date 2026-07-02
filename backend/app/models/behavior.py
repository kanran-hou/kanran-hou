"""用户行为埋点表模型"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UsersBehaviorLog(Base):
   __tablename__ = "users_behavior_log"

   id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
   user_openid: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
   action_type: Mapped[str] = mapped_column(String(32), nullable=False)
   action_detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
   analysis_id: Mapped[int | None] = mapped_column(
       BigInteger, ForeignKey("copywriting_analysis.id"), nullable=True
   )
   created_at: Mapped[datetime] = mapped_column(
       DateTime, server_default=func.now(), nullable=False
   )
