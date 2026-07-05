from pydantic import BaseModel, Field
from typing import Optional, List
class AnalyzeRequest(BaseModel):
    original_text: str = Field(..., max_length=5000)
    track_type: str = Field(..., pattern="^(xiaohongshu|ecommerce|local_tourism|short_video)$")
    user_openid: str = Field(default="")
class DimensionScore(BaseModel):
    id: str
    name: str
    score: float = 0
    grade: str = "B"
    conclusion: str = ""
class AnalyzeResponse(BaseModel):
    id: int = 0
    overall_score: float = 0
    overall_grade: str = "B"
    word_count: int = 0
    dimensions: List[DimensionScore] = []
    analysis_raw: dict = {}
