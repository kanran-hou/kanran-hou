from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter()
class FeedbackRequest(BaseModel):
    user_openid: str = ""
    analysis_id: int = 0
    feedback_type: str = ""
    feedback_text: str = ""
@router.post("/api/v1/feedback")
async def submit_feedback(req: FeedbackRequest):
    return {"code": 0, "message": "success", "data": {}}
