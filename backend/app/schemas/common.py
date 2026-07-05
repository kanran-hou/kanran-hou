from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List
T = TypeVar("T")
class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: Optional[T] = None
