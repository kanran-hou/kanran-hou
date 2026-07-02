"""LLM 调用日志记录模块"""

from __future__ import annotations

from datetime import datetime, timezone

from loguru import logger


class LLMCallLog:
    """单次 LLM 调用的结构化日志"""

    def __init__(
        self,
        provider: str,
        model: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        elapsed: float = 0.0,
        status: str = "success",
        error: str | None = None,
    ) -> None:
        self.provider = provider
        self.model = model
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.elapsed = elapsed
        self.status = status
        self.error = error
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def log(self) -> None:
        """输出结构化日志（JSON 格式）"""
        record = {
            "event": "llm_call",
            "provider": self.provider,
            "model": self.model,
            "tokens": self.prompt_tokens + self.completion_tokens,
            "elapsed_s": round(self.elapsed, 3),
            "status": self.status,
        }
        if self.error:
            record["error"] = self.error
        logger.info("LLM Call: {record}", record=record)


class AsyncCallLogger:
    """异步调用上下文管理器，自动记录耗时和结果"""

    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model
        self._start: float | None = None

    async def __aenter__(self) -> "AsyncCallLogger":
        import time
        self._start = time.perf_counter()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        import time
        elapsed = time.perf_counter() - self._start if self._start else 0.0
        status = "error" if exc_type else "success"
        log = LLMCallLog(
            provider=self.provider,
            model=self.model,
            elapsed=elapsed,
            status=status,
            error=str(exc_val) if exc_val else None,
        )
        log.log()
