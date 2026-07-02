"""向量知识库引擎 — 基于 jieba 分词 + numpy TF-IDF + 余弦相似度
   轻量实现，无需外部模型下载。后续可无缝替换为 sentence-transformers + Faiss。
"""

from __future__ import annotations

import math
import pickle
from pathlib import Path
from typing import Any

import jieba
import numpy as np

from app.services.knowledge.seeder import get_seed_templates


class TfidfVectorizer:
    """手动实现 TF-IDF 向量化（基于 jieba + numpy）"""

    def __init__(self) -> None:
        self.vocab: dict[str, int] = {}
        self.idf: dict[str, float] = {}
        self.doc_count: int = 0

    def tokenize(self, text: str) -> list[str]:
        return list(jieba.cut(text))

    def _compute_tf(self, tokens: list[str]) -> dict[str, float]:
        tf: dict[str, float] = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        return tf

    def fit(self, documents: list[str]) -> None:
        df: dict[str, int] = {}
        for doc in documents:
            tokens = set(self.tokenize(doc))
            for token in tokens:
                df[token] = df.get(token, 0) + 1
        self.doc_count = len(documents)
        self.vocab = {word: idx for idx, word in enumerate(sorted(df.keys()))}
        self.idf = {
            word: math.log((self.doc_count + 1) / (freq + 1)) + 1
            for word, freq in df.items()
        }

    def transform(self, documents: list[str]) -> np.ndarray:
        n_docs = len(documents)
        n_features = len(self.vocab)
        matrix = np.zeros((n_docs, n_features), dtype=np.float32)
        for i, doc in enumerate(documents):
            tokens = self.tokenize(doc)
            tf = self._compute_tf(tokens)
            max_tf = max(tf.values()) if tf else 1.0
            for token, freq in tf.items():
                if token in self.vocab:
                    tfidf = (freq / max_tf) * self.idf.get(token, 1.0)
                    matrix[i, self.vocab[token]] = tfidf
        return matrix


class KnowledgeService:
    """知识库检索服务

    工作流程：
    1. 服务启动时从种子数据构建 TF-IDF 向量索引
    2. 查询时对输入文本做同赛道过滤 + 余弦相似度排序
    3. 返回 Top-K 模板
    """

    _instance: KnowledgeService | None = None

    def __init__(self, index_dir: str | Path = "data/knowledge") -> None:
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # 模板数据：list[dict]
        self.templates: list[dict[str, Any]] = []
        # 按赛道分组的索引
        self._track_indices: dict[str, dict[str, Any]] = {}
        # TF-IDF 向量器
        self._vectorizer = TfidfVectorizer()
        self._initialized = False

    @classmethod
    def get_instance(cls) -> KnowledgeService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self, force_rebuild: bool = False) -> None:
        if self._initialized and not force_rebuild:
            return

        # 加载种子数据
        self.templates = get_seed_templates()
        if not self.templates:
            import warnings
            warnings.warn("知识库种子数据为空，无法构建索引")
            self._initialized = True
            return

        # 按赛道分组
        tracks = {"xiaohongshu": [], "ecommerce": [], "local_tourism": [], "short_video": []}
        for tmpl in self.templates:
            t = tmpl.get("track_type", "xiaohongshu")
            if t in tracks:
                tracks[t].append(tmpl)

        # 为每个赛道构建独立的 TF-IDF 索引
        for track, items in tracks.items():
            if not items:
                continue
            documents = [
                f"{item.get('title', '')} {' '.join(item.get('tags', []))} {item.get('content', '')[:200]}"
                for item in items
            ]
            vectorizer = TfidfVectorizer()
            vectorizer.fit(documents)
            vectors = vectorizer.transform(documents)
            self._track_indices[track] = {
                "templates": items,
                "vectorizer": vectorizer,
                "vectors": vectors,
            }

        self._initialized = True

    def search(
        self,
        query: str,
        track_type: str | None = None,
        top_k: int = 5,
        min_score: float = 0.05,
    ) -> list[dict[str, Any]]:
        if not self._initialized:
            self.initialize()

        results: list[dict[str, Any]] = []

        # 确定要搜索的赛道
        tracks_to_search = [track_type] if track_type and track_type in self._track_indices else list(self._track_indices.keys())

        for track in tracks_to_search:
            idx = self._track_indices.get(track)
            if not idx or idx["vectors"].shape[0] == 0:
                continue

            vectorizer: TfidfVectorizer = idx["vectorizer"]
            query_vec = vectorizer.transform([query])[0]

            # 计算与所有模板的余弦相似度
            sims = self._cosine_similarity(query_vec, idx["vectors"])

            # 取 Top-K
            top_indices = np.argsort(sims)[::-1][:top_k]

            for rank_pos, i in enumerate(top_indices):
                score = float(sims[i])
                if score < min_score:
                    continue
                tmpl = idx["templates"][i]
                results.append({
                    "rank": len(results) + 1,
                    "score": round(score, 4),
                    "track_type": track,
                    "title": tmpl.get("title", ""),
                    "content": tmpl.get("content", "")[:200],
                    "tags": tmpl.get("tags", []),
                    "overall_score": tmpl.get("overall_score", 0),
                    "source": tmpl.get("source", ""),
                })

            # 如果指定了赛道，只搜索该赛道
            if track_type:
                break

        # 按相似度排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    @staticmethod
    def _cosine_similarity(vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        dot = np.dot(matrix, vec)
        norm_v = np.linalg.norm(vec)
        norm_m = np.linalg.norm(matrix, axis=1)
        denom = norm_m * norm_v
        denom[denom == 0] = 1.0
        return dot / denom

    def get_top_templates(self, track_type: str, limit: int = 5) -> list[dict[str, Any]]:
        """获取指定赛道的 Top 高分模板"""
        if not self._initialized:
            self.initialize()
        items = self._track_indices.get(track_type, {}).get("templates", [])
        items_sorted = sorted(items, key=lambda x: x.get("overall_score", 0), reverse=True)
        return [
            {"title": item.get("title", ""), "score": item.get("overall_score", 0), "tags": item.get("tags", [])}
            for item in items_sorted[:limit]
        ]