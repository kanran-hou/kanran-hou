"""Initial database schema

Revision ID: 0001
Revises:
Create Date: 2026-07-01
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
   # copywriting_analysis 表
   op.create_table(
       "copywriting_analysis",
       sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
       sa.Column("user_openid", sa.String(64), nullable=False),
       sa.Column("original_text", mysql.LONGTEXT(), nullable=False),
       sa.Column(
           "track_type",
           sa.Enum("xiaohongshu", "ecommerce", "local_tourism", "short_video", name="track_type_enum"),
           nullable=False,
       ),
       sa.Column("title_score", sa.Float(precision=5, asdecimal=True), nullable=True),
       sa.Column("emotion_score", sa.Float(precision=5, asdecimal=True), nullable=True),
       sa.Column("structure_score", sa.Float(precision=5, asdecimal=True), nullable=True),
       sa.Column("audience_score", sa.Float(precision=5, asdecimal=True), nullable=True),
       sa.Column("overall_score", sa.Float(precision=5, asdecimal=True), nullable=True),
       sa.Column(
           "overall_grade",
           sa.Enum("S", "A", "B", "C", name="overall_grade_enum"),
           nullable=True,
       ),
       sa.Column("analysis_raw", mysql.JSON(), nullable=True),
       sa.Column("word_count", sa.Integer(), nullable=True),
       sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
       sa.PrimaryKeyConstraint("id"),
       mysql_charset="utf8mb4",
       mysql_collate="utf8mb4_unicode_ci",
       mysql_engine="InnoDB",
   )
   op.create_index(op.f("ix_copywriting_analysis_user_openid"), "copywriting_analysis", ["user_openid"])
   op.create_index(op.f("ix_copywriting_analysis_track_type"), "copywriting_analysis", ["track_type"])

   # users_behavior_log 表
   op.create_table(
       "users_behavior_log",
       sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
       sa.Column("user_openid", sa.String(64), nullable=False),
       sa.Column("action_type", sa.String(32), nullable=False),
       sa.Column("action_detail", mysql.JSON(), nullable=True),
       sa.Column("analysis_id", sa.BigInteger(), nullable=True),
       sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
       sa.PrimaryKeyConstraint("id"),
       mysql_charset="utf8mb4",
       mysql_collate="utf8mb4_unicode_ci",
       mysql_engine="InnoDB",
   )
   op.create_index(op.f("ix_users_behavior_log_user_openid"), "users_behavior_log", ["user_openid"])
   op.create_index(op.f("ix_users_behavior_log_action_type"), "users_behavior_log", ["action_type"])
   op.create_foreign_key(
       "fk_behavior_analysis", "users_behavior_log", "copywriting_analysis",
       ["analysis_id"], ["id"], ondelete="SET NULL",
   )

   # user_feedback 表
   op.create_table(
       "user_feedback",
       sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
       sa.Column("user_openid", sa.String(64), nullable=False),
       sa.Column("analysis_id", sa.BigInteger(), nullable=True),
       sa.Column("feedback_type", sa.String(32), nullable=False),
       sa.Column("feedback_text", sa.Text(), nullable=True),
       sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
       sa.PrimaryKeyConstraint("id"),
       mysql_charset="utf8mb4",
       mysql_collate="utf8mb4_unicode_ci",
       mysql_engine="InnoDB",
   )
   op.create_index(op.f("ix_user_feedback_user_openid"), "user_feedback", ["user_openid"])
   op.create_index(op.f("ix_user_feedback_feedback_type"), "user_feedback", ["feedback_type"])
   op.create_foreign_key(
       "fk_feedback_analysis", "user_feedback", "copywriting_analysis",
       ["analysis_id"], ["id"], ondelete="SET NULL",
   )


def downgrade() -> None:
   op.drop_table("user_feedback")
   op.drop_table("users_behavior_log")
   op.drop_table("copywriting_analysis")
   op.execute("DROP TYPE IF EXISTS track_type_enum")
   op.execute("DROP TYPE IF EXISTS overall_grade_enum")
