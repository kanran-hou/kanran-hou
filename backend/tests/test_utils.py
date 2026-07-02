"""工具函数测试"""

from __future__ import annotations

from app.utils.time_utils import now_utc, now_cst, utc_to_cst
from app.utils.string_utils import count_chars, split_paragraphs


def test_count_chars():
   """字数统计测试"""
   assert count_chars("Hello World") == 2
   assert count_chars("你好世界") == 4
   assert count_chars("你好 Hello 世界 World") == 6
   assert count_chars("") == 0


def test_split_paragraphs():
   """段落分割测试"""
   text = "第一段内容。\n\n第二段内容。\n\n第三段内容。"
   result = split_paragraphs(text)
   assert len(result) == 3
   assert result[0] == "第一段内容。"


def test_split_long_paragraph():
   """超长段落分割测试"""
   long_text = "这是第一句。" + "这是额外填充内容。" * 50 + "这是最后一句。"
   result = split_paragraphs(long_text, max_length=50)
   assert len(result) > 1
   assert "这是第一句。" in result[0]


def test_now_utc():
   """UTC 时间函数测试"""
   dt = now_utc()
   assert dt.tzinfo is not None


def test_now_cst():
   """东八区时间函数测试"""
   dt = now_cst()
   assert dt.utcoffset().total_seconds() == 8 * 3600


def test_utc_to_cst():
   """UTC 转东八区测试"""
   from datetime import datetime, timezone
   utc_dt = datetime(2026, 7, 1, 0, 0, 0, tzinfo=timezone.utc)
   cst_dt = utc_to_cst(utc_dt)
   assert cst_dt.hour == 8
