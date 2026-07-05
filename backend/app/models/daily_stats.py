from sqlalchemy import Column, BigInteger, String, Integer, Date, JSON, DateTime
from app.database import Base

class DailyStats(Base):
    __tablename__ = "daily_stats"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    stat_date = Column(Date)
    track_type = Column(String(32))
    analyze_count = Column(Integer, default=0)
    avg_score = Column(Integer, default=0)
    extra = Column(JSON)
    created_at = Column(DateTime)
