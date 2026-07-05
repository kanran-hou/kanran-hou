from pydantic import BaseModel
from typing import Optional
class TitleAnalysis(BaseModel):
    score: int = 0
    comment: str = ""
class EmotionAnalysis(BaseModel):
    score: int = 0
    comment: str = ""
class AnalysisResult(BaseModel):
    title: TitleAnalysis = TitleAnalysis()
    emotion: EmotionAnalysis = EmotionAnalysis()
    overall_score: int = 0
