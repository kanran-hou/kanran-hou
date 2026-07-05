from fastapi import APIRouter
router = APIRouter()
@router.get("/api/v1/knowledge")
async def get_knowledge(track_type: str = "", keyword: str = "", page: int = 1, page_size: int = 20):
    return {"code": 0, "message": "success", "data": {"items": [], "total": 0, "page": page, "page_size": page_size}}
@router.post("/api/v1/knowledge/seed")
async def seed_knowledge():
    return {"code": 0, "message": "seeded"}
