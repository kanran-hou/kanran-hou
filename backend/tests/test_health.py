"""健康检查端点测试"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
   """GET /api/v1/health 应返回 200 和正确状态"""
   response = await client.get("/api/v1/health")
   assert response.status_code == 200
   data = response.json()
   assert data["status"] == "ok"
   assert "timestamp" in data
   assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_health_method_not_allowed(client: AsyncClient) -> None:
   """POST /api/v1/health 应返回 405"""
   response = await client.post("/api/v1/health")
   assert response.status_code == 405


@pytest.mark.asyncio
async def test_not_found(client: AsyncClient) -> None:
   """不存在的路径应返回 404"""
   response = await client.get("/api/v1/nonexistent")
   assert response.status_code == 404
   data = response.json()
   assert data["code"] == 404
