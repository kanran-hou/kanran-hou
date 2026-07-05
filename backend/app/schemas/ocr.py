from pydantic import BaseModel
from typing import Optional, List
class OCRRequest(BaseModel):
    image_base64: str = ""
    image_url: str = ""
class OCRResponse(BaseModel):
    text: str = ""
    confidence: float = 0
    words: List[dict] = []
