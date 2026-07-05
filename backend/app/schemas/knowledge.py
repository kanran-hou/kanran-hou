from pydantic import BaseModel
from typing import Optional, List
class KnowledgeItem(BaseModel):
    id: int
    track_type: str
    title: str
    content: str
    score: int = 0
    tags: List[str] = []
class KnowledgeQuery(BaseModel):
    track_type: Optional[str] = None
    keyword: str = ""
    page: int = 1
    page_size: int = 20
