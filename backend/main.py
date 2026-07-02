"""CopyMind Backend — FastAPI 应用入口"""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_log import RequestLogMiddleware
from app.routers.health import router as health_router
from app.routers.analyze import router as analyze_router
from app.routers.knowledge import router as knowledge_router
from app.routers.ocr import router as ocr_router
from app.routers.history import router as history_router
from app.routers.feedback import router as feedback_router
from app.routers.admin import router as admin_router

# ---- 定时任务 ----
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.scheduler import compute_daily_stats
from app.services.cluster_feedback import run_clustering

scheduler = AsyncIOScheduler()


# ---- 日志配置 ----
def setup_logging() -> None:
   log_dir = Path("logs")
   log_dir.mkdir(exist_ok=True)

   logger.remove()  # 清除默认 handler
   logger.add(
       sys.stdout,
       level=settings.LOG_LEVEL,
       format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
   )
   logger.add(
       settings.LOG_FILE,
       level=settings.LOG_LEVEL,
       rotation="10 MB",
       retention="30 days",
       encoding="utf-8",
   )


# ---- 生命周期 ----
@asynccontextmanager
async def lifespan(app: FastAPI):
   setup_logging()
   logger.info("CopyMind Backend starting up (env={env})", env=settings.ENV)
   # ---- 启动定时任务 ----
   scheduler.add_job(compute_daily_stats, 'cron', hour=settings.DAILY_STATS_SCHEDULE_HOUR, minute=settings.DAILY_STATS_SCHEDULE_MINUTE, id='daily_stats')
   scheduler.add_job(run_clustering, 'cron', day_of_week='mon', hour=4, minute=0, id='weekly_clustering')
   scheduler.start()
   logger.info('Scheduler started: daily_stats={h}:{m}, weekly_clustering=Mon 4:00')
   yield
   scheduler.shutdown(wait=False)
   logger.info('Scheduler shut down')
   logger.info("CopyMind Backend shutting down")


# ---- 应用实例 ----
app = FastAPI(
   title="CopyMind API",
   description="CopyMind AI 文案智能分析后端服务",
   version="0.1.0",
   lifespan=lifespan,
   docs_url="/docs" if settings.DEBUG else None,
   redoc_url="/redoc" if settings.DEBUG else None,
)

# ---- CORS ----
app.add_middleware(
   CORSMiddleware,
   allow_origins=settings.cors_origins_list,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

# ---- 自定义中间件 ----
app.add_middleware(RequestLogMiddleware)
app.add_middleware(RateLimitMiddleware)

# ---- 路由注册 ----
api_prefix = "/api/v1"
app.include_router(health_router, prefix=api_prefix)
app.include_router(analyze_router)
app.include_router(knowledge_router)
app.include_router(ocr_router)
app.include_router(history_router)
app.include_router(feedback_router)
app.include_router(admin_router)


# ---- 全局异常处理器（占位，随 Phase 扩展） ----
@app.exception_handler(404)
async def not_found_handler(request, exc):
   from fastapi.responses import JSONResponse
   return JSONResponse(
       status_code=404,
       content={"code": 404, "message": "接口不存在", "data": None},
   )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
   from fastapi.responses import JSONResponse
   logger.error("Internal server error: {exc}", exc=exc)
   return JSONResponse(
       status_code=500,
       content={"code": 500, "message": "服务器内部错误", "data": None},
   )


if __name__ == "__main__":
   import uvicorn
   uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
