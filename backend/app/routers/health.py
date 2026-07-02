"""健康检查端点"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
   """服务健康检查"""
   return HealthResponse(
       status="ok",
       timestamp=datetime.now(timezone.utc).isoformat(),
       version="0.1.0",
   )
