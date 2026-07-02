"""Phase 6: users, daily_stats, feedback_clusters tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-02
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users 表
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_openid", sa.String(64), nullable=False),
        sa.Column(
            "tier",
            sa.Enum("normal", "frequent", "vip", name="user_tier_enum"),
            nullable=False,
            server_default="normal",
        ),
        sa.Column("daily_analysis_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_analysis_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index(op.f("ix_users_user_openid"), "users", ["user_openid"], unique=True)

    # daily_stats 表
    op.create_table(
        "daily_stats",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("stat_date", sa.Date(), nullable=False),
        sa.Column("total_analysis", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_overall_score", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("grade_distribution", mysql.JSON(), nullable=True),
        sa.Column("track_distribution", mysql.JSON(), nullable=True),
        sa.Column("active_users", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stat_date"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )

    # feedback_clusters 表
    op.create_table(
        "feedback_clusters",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("cluster_id", sa.Integer(), nullable=False),
        sa.Column("cluster_label", sa.String(64), nullable=True),
        sa.Column("sample_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sample_texts", mysql.JSON(), nullable=True),
        sa.Column("created_week", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index(op.f("ix_feedback_clusters_created_week"), "feedback_clusters", ["created_week"])


def downgrade() -> None:
    op.drop_table("feedback_clusters")
    op.drop_table("daily_stats")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS user_tier_enum")
