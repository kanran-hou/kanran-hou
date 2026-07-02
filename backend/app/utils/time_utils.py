"""时间工具函数 — UTC / 东八区转换"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

# 东八区时区
CST = timezone(timedelta(hours=8), name="Asia/Shanghai")


def now_utc() -> datetime:
   """获取当前 UTC 时间"""
   return datetime.now(timezone.utc)


def now_cst() -> datetime:
   """获取当前东八区时间"""
   return datetime.now(CST)


def utc_to_cst(dt: datetime) -> datetime:
   """将 UTC datetime 转换为东八区 datetime"""
   if dt.tzinfo is None:
       dt = dt.replace(tzinfo=timezone.utc)
   return dt.astimezone(CST)


def cst_to_utc(dt: datetime) -> datetime:
   """将东八区 datetime 转换为 UTC"""
   if dt.tzinfo is None:
       dt = dt.replace(tzinfo=CST)
   return dt.astimezone(timezone.utc)


def format_time(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
   """格式化时间为字符串"""
   return dt.strftime(fmt)
