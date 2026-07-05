from sqlalchemy import Column, BigInteger, String, Text, DateTime
from app.database import Base

class Feedback(Base):
    __tablename__ = "user_feedback"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_openid = Column(String(64))
    analysis_id = Column(BigInteger)
    feedback_type = Column(String(32))
    feedback_text = Column(Text)
    created_at = Column(DateTime)
