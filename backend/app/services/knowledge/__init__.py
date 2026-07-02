"""知识库服务包"""
from app.services.knowledge.engine import KnowledgeService
from app.services.knowledge.seeder import get_seed_templates

__all__ = ["KnowledgeService", "get_seed_templates"]
