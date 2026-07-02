"""请求限流中间件 — 基于令牌桶算法的简单实现"""

from __future__ import annotations

import time

from fastapi import Request, HTTPException
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import settings


class TokenBucket:
   """令牌桶限流算法"""

   def __init__(self, rate: int, burst: int | None = None) -> None:
       self.rate = rate  # 每秒令牌数
       self.burst = burst or rate  # 桶容量上限
       self.tokens = float(self.burst)
       self.last_refill = time.monotonic()

   def consume(self, tokens: int = 1) -> bool:
       """消耗 tokens 个令牌，返回是否允许通过"""
       now = time.monotonic()
       elapsed = now - self.last_refill
       self.last_refill = now

       # 按时间增量补充令牌
       self.tokens = min(float(self.burst), self.tokens + elapsed * self.rate)

       if self.tokens >= tokens:
           self.tokens -= tokens
           return True
       return False


# 全局实例：根据配置初始化（RATE_LIMIT_PER_MINUTE 转换为每秒）
_bucket = TokenBucket(rate=settings.RATE_LIMIT_PER_MINUTE / 60.0)


class RateLimitMiddleware(BaseHTTPMiddleware):
   """全局限流中间件"""

   async def dispatch(
       self, request: Request, call_next: RequestResponseEndpoint
   ) -> Response:
       # 跳过健康检查的限流
       if request.url.path == "/health":
           return await call_next(request)

       if not _bucket.consume():
           logger.warning("Rate limit exceeded for {path}", path=request.url.path)
           raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")

       return await call_next(request)
