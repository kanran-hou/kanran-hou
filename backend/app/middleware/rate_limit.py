import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = {}
    async def dispatch(self, request: Request, call_next):
        if request.url.path.endswith("/health") or request.url.path.endswith("/docs"):
            return await call_next(request)
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        cutoff = now - self.window
        if client_ip in self.requests:
            self.requests[client_ip] = [t for t in self.requests[client_ip] if t > cutoff]
        else:
            self.requests[client_ip] = []
        if len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(status_code=429, content={"code":429,"message":"rate limit exceeded"})
        self.requests[client_ip].append(now)
        return await call_next(request)
