"""OCR 识别相关 Pydantic schemas"""

from __future__ import annotations

from pydantic import BaseModel, Field


class OcrRequest(BaseModel):
    """OCR 识别请求"""
    image_base64: str | None = Field(None, description="Base64 编码的图片")
    post_process: bool = Field(True, description="是否执行后处理过滤")


class OcrResponse(BaseModel):
    """OCR 识别响应"""
    text: str = ""
    word_count: int = 0
    available: bool = False
    message: str = ""