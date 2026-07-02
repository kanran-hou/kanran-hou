"""数据库连接池配置 — SQLAlchemy 2.0 async session"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(
   settings.DATABASE_URL,
   pool_size=10,
   max_overflow=20,
   pool_pre_ping=True,
   echo=settings.DEBUG,
)

async_session_factory = async_sessionmaker(
   engine,
   class_=AsyncSession,
   expire_on_commit=False,
)


class Base(DeclarativeBase):
   """SQLAlchemy 声明式基类"""


async def get_db() -> AsyncSession:
   """FastAPI 依赖注入：获取数据库会话"""
   async with async_session_factory() as session:
       try:
           yield session
           await session.commit()
       except Exception:
           await session.rollback()
           raise
       finally:
           await session.close()
