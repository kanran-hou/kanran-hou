"""测试配置与共享 fixtures"""

from __future__ import annotations

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.database import Base, engine, async_session_factory
from main import app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
   """FastAPI 测试客户端"""
   transport = ASGITransport(app=app)
   async with AsyncClient(transport=transport, base_url="http://test") as ac:
       yield ac


@pytest_asyncio.fixture
async def db_session():
   """数据库测试会话（使用内存 SQLite 或单独测试库）"""
   async with async_session_factory() as session:
       yield session
       await session.rollback()


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
   """测试环境变量"""
   monkeypatch.setenv("ENV", "test")
   monkeypatch.setenv("DEBUG", "false")
   monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "1000")  # 测试环境不限流
