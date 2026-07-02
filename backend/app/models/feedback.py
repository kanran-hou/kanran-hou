"""用户反馈表模型"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserFeedback(Base):
   __tablename__ = "user_feedback"

   id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
   user_openid: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
   analysis_id: Mapped[int | None] = mapped_column(
       BigInteger, ForeignKey("copywriting_analysis.id"), nullable=True
   )
   feedback_type: Mapped[str] = mapped_column(String(32), nullable=False)
   feedback_text: Mapped[str | None] = mapped_column(Text, nullable=True)
   processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
   created_at: Mapped[datetime] = mapped_column(
       DateTime, server_default=func.now(), nullable=False
   )
