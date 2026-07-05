from fastapi import APIRouter
from datetime import datetime
router = APIRouter()
@router.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
@router.get("/api/v1/health")
async def health_check_v1():
    return {"code": 0, "message": "success", "data": {"status": "ok", "timestamp": datetime.now().isoformat()}}
