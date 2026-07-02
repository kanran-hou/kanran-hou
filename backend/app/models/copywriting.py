"""文案分析与结果表模型"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, Float, Integer, String, func
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CopywritingAnalysis(Base):
   __tablename__ = "copywriting_analysis"

   id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
   user_openid: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
   original_text: Mapped[str] = mapped_column(LONGTEXT, nullable=False)
   track_type: Mapped[str] = mapped_column(
       Enum(
           "xiaohongshu",
           "ecommerce",
           "local_tourism",
           "short_video",
           name="track_type_enum",
       ),
       nullable=False,
   )
   title_score: Mapped[float | None] = mapped_column(Float(5, 2), nullable=True)
   emotion_score: Mapped[float | None] = mapped_column(Float(5, 2), nullable=True)
   structure_score: Mapped[float | None] = mapped_column(Float(5, 2), nullable=True)
   audience_score: Mapped[float | None] = mapped_column(Float(5, 2), nullable=True)
   overall_score: Mapped[float | None] = mapped_column(Float(5, 2), nullable=True)
   overall_grade: Mapped[str | None] = mapped_column(
       Enum("S", "A", "B", "C", name="overall_grade_enum"), nullable=True
   )
   analysis_raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)
   word_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
   created_at: Mapped[datetime] = mapped_column(
       DateTime, server_default=func.now(), nullable=False
   )
