from sqlalchemy import Column, BigInteger, String, Text, DateTime, Float, JSON, Integer
from app.database import Base

class Copywriting(Base):
    __tablename__ = "copywriting_analysis"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_openid = Column(String(64))
    original_text = Column(Text)
    track_type = Column(String(32))
    title_score = Column(Float, default=0)
    emotion_score = Column(Float, default=0)
    structure_score = Column(Float, default=0)
    audience_score = Column(Float, default=0)
    overall_score = Column(Float, default=0)
    overall_grade = Column(String(8), default="B")
    analysis_raw = Column(JSON)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime)
