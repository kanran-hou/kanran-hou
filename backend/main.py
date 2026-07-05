from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

from app.routers import health_router, analyze_router, history_router, feedback_router, ocr_router, knowledge_router, admin_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_log import RequestLogMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-6s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("copymind")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== CopyMind Backend Starting ===")
    try:
        from app.database import init_db
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database skipped: {e}")
    yield
    logger.info("=== CopyMind Backend Stopped ===")

app = FastAPI(title="CopyMind AI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLogMiddleware)

app.include_router(health_router)
app.include_router(analyze_router)
app.include_router(history_router)
app.include_router(feedback_router)
app.include_router(ocr_router)
app.include_router(knowledge_router)
app.include_router(admin_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

from app.routers import health_router, analyze_router, history_router, feedback_router, ocr_router, knowledge_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_log import RequestLogMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-6s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("copymind")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== CopyMind Backend Starting ===")
    try:
        from app.database import init_db
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database skipped: {e}")
    yield
    logger.info("=== CopyMind Backend Stopped ===")

app = FastAPI(title="CopyMind AI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLogMiddleware)

app.include_router(health_router)
app.include_router(analyze_router)
app.include_router(history_router)
app.include_router(feedback_router)
app.include_router(ocr_router)
app.include_router(knowledge_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
