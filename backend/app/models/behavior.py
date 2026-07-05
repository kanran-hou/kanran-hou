from sqlalchemy import Column, BigInteger, String, JSON, DateTime
from app.database import Base

class BehaviorLog(Base):
    __tablename__ = "users_behavior_log"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_openid = Column(String(64))
    action_type = Column(String(32))
    action_detail = Column(JSON)
    analysis_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime)
