from fastapi import APIRouter
router = APIRouter()
@router.post("/api/v1/ocr")
async def ocr_recognize():
    return {"code": 0, "message": "OCR not enabled", "data": {"text": ""}}
