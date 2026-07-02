"""OCR 识别 API — POST /api/v1/ocr/recognize"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile, File
from loguru import logger

from app.schemas.common import ApiResponse
from app.schemas.ocr import OcrResponse
from app.services.ocr import ocr_service

router = APIRouter(prefix="/api/v1/ocr", tags=["ocr"])

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}


@router.post("/recognize", response_model=ApiResponse[OcrResponse])
async def recognize_image(image: UploadFile = File(...)):
    """上传图片并识别文字"""
    # 校验文件类型
    ext = f".{image.filename.split('.')[-1].lower()}" if "." in image.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式 '{ext}'，支持: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # 读取图片
    data = await image.read()

    # 校验大小
    if len(data) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"图片大小超过 5MB 限制（当前约 {len(data) / 1024 / 1024:.1f}MB）",
        )

    try:
        result = ocr_service.recognize(data)
        return ApiResponse(data=OcrResponse(
            text=result.get("text", ""),
            word_count=result.get("word_count", 0),
            available=result.get("available", False),
            message=result.get("message", ""),
        ))
    except Exception as e:
        logger.error("OCR recognition error: {e}", e=e)
        return ApiResponse(
            code=500,
            message=f"识别失败: {str(e)}",
            data=OcrResponse(available=False, message=f"识别失败: {str(e)}"),
        )