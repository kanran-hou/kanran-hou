"""知识库检索 API — POST /api/v1/knowledge/search"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.knowledge import ReferenceCase, SearchRequest, SearchResponse, TemplateMatch
from app.services.knowledge import KnowledgeService

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


@router.post("/search", response_model=ApiResponse[SearchResponse])
async def search_templates(
    req: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """搜索同赛道高分文案模板"""
    try:
        svc = KnowledgeService.get_instance()
        svc.initialize()
        results = svc.search(
            query=req.query,
            track_type=req.track_type,
            top_k=req.top_k,
        )
        templates = [
            TemplateMatch(
                rank=r["rank"],
                score=r["score"],
                track_type=r["track_type"],
                title=r["title"],
                content=r["content"],
                tags=r["tags"],
                overall_score=r.get("overall_score", 0),
                source=r.get("source", ""),
            )
            for r in results
        ]
        return ApiResponse(data=SearchResponse(
            templates=templates,
            total=len(templates),
            query_track=req.track_type,
        ))
    except Exception as e:
        logger.error("Knowledge search error: {e}", e=e)
        return ApiResponse(code=500, message=f"搜索失败: {str(e)}", data=SearchResponse())


@router.get("/top", response_model=ApiResponse[list[ReferenceCase]])
async def get_top_templates(
    track_type: str = "xiaohongshu",
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
):
    """获取指定赛道的高分参考模板"""
    try:
        svc = KnowledgeService.get_instance()
        svc.initialize()
        items = svc.get_top_templates(track_type, limit)
        cases = [
            ReferenceCase(title=item["title"], score=item["score"], tags=item["tags"])
            for item in items
        ]
        return ApiResponse(data=cases)
    except Exception as e:
        logger.error("Get top templates error: {e}", e=e)
        return ApiResponse(code=500, message=str(e), data=[])