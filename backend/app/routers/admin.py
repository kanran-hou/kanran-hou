from fastapi import APIRouter
from datetime import datetime
router = APIRouter()
@router.get("/api/v1/admin/stats")
async def admin_stats():
    return {"code": 0, "message": "success", "data": {"total_analyzes": 0, "today_count": 0, "avg_score": 0}}
@router.get("/admin/dashboard")
async def admin_dashboard():
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content="<html><body><h1>CopyMind Admin</h1></body></html>")
