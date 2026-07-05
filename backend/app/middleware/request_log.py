import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
logger = logging.getLogger("copymind.access")
class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)
        logger.info(f"{request.method} {request.url.path} {response.status_code} {duration_ms}ms")
        return response
