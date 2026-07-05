from fastapi import APIRouter
router = APIRouter()
@router.get("/api/v1/history")
async def get_history(page: int = 1, page_size: int = 20, user_openid: str = ""):
    return {"code": 0, "message": "success", "data": {"items": [], "total": 0, "page": page, "page_size": page_size}}
