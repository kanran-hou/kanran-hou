"""文本聚类脚本 — 对用户反馈进行聚类分析

用法:
    python -m app.services.cluster_feedback

输出:
    - 写入 feedback_clusters 表
    - 生成 docs/feedback-report-weekly.md
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import date
from pathlib import Path

from loguru import logger


# ---- 可选依赖兼容 ----
try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    logger.warning("jieba not installed; clustering will use simple keyword grouping")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not installed; clustering will use simple rule-based grouping")

from sqlalchemy import select, func, delete

from app.database import async_session_factory
from app.models.feedback import UserFeedback
from app.models.feedback_clusters import FeedbackCluster


async def fetch_feedback_texts() -> list[dict]:
    """从 user_feedback 表读取 feedback_text """
    async with async_session_factory() as db:
        q = select(UserFeedback).where(
            UserFeedback.feedback_text.isnot(None),
            UserFeedback.feedback_text != "",
        )
        r = await db.execute(q)
        rows = r.scalars().all()
        return [{"id": row.id, "text": row.feedback_text, "type": row.feedback_type} for row in rows]


def _get_current_week() -> str:
    """返回 ISO 周格式，如 2026-W27"""
    d = date.today()
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def _simple_grouping(items: list[dict]) -> list[dict]:
    """基于反馈类型的简单分组（降级方案）"""
    groups: dict[str, list[str]] = {}
    for item in items:
        t = item["type"]
        if t not in groups:
            groups[t] = []
        groups[t].append(item["text"])

    label_map = {
        "analysis_inaccurate": "分析结果不准确",
        "suggestion_invalid": "优化建议无效",
        "other": "其他反馈",
    }

    clusters = []
    for i, (ftype, texts) in enumerate(groups.items()):
        clusters.append({
            "cluster_id": i + 1,
            "cluster_label": label_map.get(ftype, ftype),
            "sample_count": len(texts),
            "sample_texts": texts[:5],
        })
    return clusters


def _kmeans_clustering(items: list[dict], n_clusters: int = 4) -> list[dict]:
    """基于 jieba + TF-IDF + KMeans 的文本聚类"""
    if not items:
        return []

    texts = [i["text"] for i in items]

    # jieba 分词
    cut_texts = [" ".join(jieba.cut(t)) for t in texts]

    # TF-IDF
    vectorizer = TfidfVectorizer(max_features=500, stop_words=None)
    X = vectorizer.fit_transform(cut_texts)

    # KMeans
    k = min(n_clusters, len(set(item["type"] for item in items)), len(items))
    k = max(k, 2)
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)

    # 按聚类分组
    clusters_map: dict[int, list[str]] = {}
    for i, label in enumerate(labels):
        if label not in clusters_map:
            clusters_map[label] = []
        clusters_map[label].append(texts[i])

    # 提取每个聚类的关键词作为标签
    clusters = []
    for i, (label, text_list) in enumerate(clusters_map.items()):
        # 简单标签：取该簇中 TF-IDF 权重最高的词
        center = km.cluster_centers_[label]
        top_idx = center.argsort()[-3:][::-1]
        feature_names = vectorizer.get_feature_names_out()
        keywords = [feature_names[idx] for idx in top_idx if idx < len(feature_names)]
        label_text = " / ".join(keywords) if keywords else f"聚类 {i + 1}"

        clusters.append({
            "cluster_id": i + 1,
            "cluster_label": label_text,
            "sample_count": len(text_list),
            "sample_texts": text_list[:5],
        })

    clusters.sort(key=lambda x: x["sample_count"], reverse=True)
    return clusters


async def run_clustering() -> list[dict]:
    """执行聚类分析并写入数据库"""
    items = await fetch_feedback_texts()
    if not items:
        logger.info("No feedback texts found for clustering")
        return []

    week = _get_current_week()

    if SKLEARN_AVAILABLE and JIEBA_AVAILABLE and len(items) >= 5:
        clusters = _kmeans_clustering(items, n_clusters=min(5, len(items)))
        logger.info("KMeans clustering completed: {n} clusters", n=len(clusters))
    else:
        clusters = _simple_grouping(items)
        logger.info("Simple grouping completed: {n} groups", n=len(clusters))

    # 写入 database
    async with async_session_factory() as db:
        # 清除本周旧数据
        await db.execute(
            delete(FeedbackCluster).where(FeedbackCluster.created_week == week)
        )
        for cl in clusters:
            db.add(FeedbackCluster(
                cluster_id=cl["cluster_id"],
                cluster_label=cl["cluster_label"],
                sample_count=cl["sample_count"],
                sample_texts=cl["sample_texts"],
                created_week=week,
            ))
        await db.commit()
        logger.info("Clusters saved to database: {n} clusters for {week}", n=len(clusters), week=week)

    # 生成 Markdown 报告
    _generate_report(clusters, week)

    return clusters


def _generate_report(clusters: list[dict], week: str) -> None:
    """生成 Markdown 格式的聚类报告"""
    report_path = Path("docs") / "feedback-report-weekly.md"
    report_path.parent.mkdir(exist_ok=True)

    lines = [
        f"# 用户反馈聚类分析报告 — {week}",
        "",
        f"> 生成时间：{date.today().isoformat()}",
        f"> 聚类方法：{'KMeans (jieba + TF-IDF)' if SKLEARN_AVAILABLE and JIEBA_AVAILABLE else '规则分组'}",
        "",
        "## 聚类结果摘要",
        "",
        f"共发现 **{len(clusters)}** 个聚类类别，覆盖 {sum(c['sample_count'] for c in clusters)} 条反馈。",
        "",
    ]

    for idx, cl in enumerate(clusters):
        lines.extend([
            f"### 聚类 {idx + 1}：{cl['cluster_label']}",
            "",
            f"- **样本数量**：{cl['sample_count']}",
            "- **代表样本**：",
        ])
        for s in cl["sample_texts"]:
            lines.append(f"  - _{s}_")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 产品改进建议",
        "",
        "基于聚类结果，建议优先关注以下方向：",
        "",
    ])

    # 为每个聚类生成改进建议
    for idx, cl in enumerate(clusters):
        label = cl["cluster_label"]
        lines.extend([
            f"1. **{label}**（{cl['sample_count']} 条反馈）",
            "   - 进一步分析用户具体诉求",
            "   - 评估是否需要进行产品迭代",
            "",
        ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Cluster report written to {path}", path=report_path)


def run_clustering_sync():
    """同步入口（供 APScheduler 调用）"""
    asyncio.run(run_clustering())


if __name__ == "__main__":
    asyncio.run(run_clustering())
