"""请求日志中间件 — 记录方法、路径、耗时、状态码"""

from __future__ import annotations

import time

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class RequestLogMiddleware(BaseHTTPMiddleware):
   """记录每次请求的方法、路径、耗时和状态码"""

   async def dispatch(
       self, request: Request, call_next: RequestResponseEndpoint
   ) -> Response:
       start_time = time.perf_counter()

       response = await call_next(request)

       elapsed = time.perf_counter() - start_time
       logger.info(
           "{method} {path} -> {status} ({elapsed:.3f}s)",
           method=request.method,
           path=request.url.path,
           status=response.status_code,
           elapsed=elapsed,
       )

       return response
