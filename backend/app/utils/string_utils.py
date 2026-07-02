"""字符串工具函数 — 字数统计、分段、敏感词过滤预留"""

from __future__ import annotations

import re
from typing import Callable


def count_chars(text: str) -> int:
   """统计中文字符 + 英文单词混合场景下的近似字数"""
   # 中文字符每个算 1 字
   chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
   # 英文单词、数字、URL 等连续非中文字符块
   non_chinese_blocks = re.split(r"[\u4e00-\u9fff]+", text)
   word_count = 0
   for block in non_chinese_blocks:
       block = block.strip()
       if block:
           word_count += len(block.split())
   return chinese_chars + word_count


def split_paragraphs(text: str, max_length: int = 500) -> list[str]:
   """将长文本按段落 + 最大长度分段"""
   paragraphs = re.split(r"\n\s*\n", text.strip())
   result: list[str] = []
   for para in paragraphs:
       para = para.strip()
       if not para:
           continue
       if len(para) <= max_length:
           result.append(para)
       else:
           # 超长段落按句号切分
           sentences = re.split(r"(?<=[。！？.!?])", para)
           chunk = ""
           for sent in sentences:
               if not sent.strip():
                   continue
               if len(chunk) + len(sent) <= max_length:
                   chunk += sent
               else:
                   if chunk:
                       result.append(chunk.strip())
                   chunk = sent
           if chunk:
               result.append(chunk.strip())
   return result


# 敏感词过滤（预留）
_sensitive_words: list[str] = []


def load_sensitive_words(word_list: list[str]) -> None:
   """加载敏感词列表（Phase 2+ 接入）"""
   global _sensitive_words
   _sensitive_words = word_list


def contains_sensitive(text: str) -> bool:
   """检查文本是否包含敏感词（简单匹配）"""
   for word in _sensitive_words:
       if word in text:
           return True
   return False


def filter_sensitive(text: str, replacement: str = "***") -> str:
   """替换文本中的敏感词"""
   for word in _sensitive_words:
       text = text.replace(word, replacement)
   return text


# 重试装饰器工具（简化版，完整重试使用 tenacity）
RetryFunc = Callable[..., object]


def retry_on_failure(max_retries: int = 3, delay: float = 1.0) -> Callable[[RetryFunc], RetryFunc]:
   """简单的重试装饰器，同步函数用。
   注：异步函数请使用 tenacity 的 @retry 装饰器（已在 pyproject.toml 中引入）。
   """
   import time
   import functools

   def decorator(func: RetryFunc) -> RetryFunc:
       @functools.wraps(func)
       def wrapper(*args: object, **kwargs: object) -> object:
           last_exception: Exception | None = None
           for attempt in range(max_retries):
               try:
                   return func(*args, **kwargs)
               except Exception as e:
                   last_exception = e
                   if attempt < max_retries - 1:
                       time.sleep(delay)
           raise last_exception  # type: ignore
       return wrapper  # type: ignore
   return decorator
