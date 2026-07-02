"""统一响应模型和共用 Pydantic schemas"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
   """统一 API 响应结构"""

   code: int = 0
   message: str = "success"
   data: DataT | None = None


class PaginationMeta(BaseModel):
   """分页元数据"""

   page: int = 1
   page_size: int = 20
   total: int = 0
   total_pages: int = 0


class PaginatedResponse(ApiResponse[list[DataT]], Generic[DataT]):
   """分页响应"""

   pagination: PaginationMeta | None = None


class HealthResponse(BaseModel):
   """健康检查响应"""

   status: str = "ok"
   timestamp: str = ""
   version: str = "0.1.0"


class ErrorResponse(BaseModel):
   """错误响应详情"""

   detail: str
   error_code: str | None = None
   path: str | None = None
