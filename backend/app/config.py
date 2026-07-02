"""配置管理模块 — 基于 pydantic-settings 从 .env 加载"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
   """全局配置，自动读取 .env 文件"""

   model_config = SettingsConfigDict(
       env_file=".env",
       env_file_encoding="utf-8",
       case_sensitive=False,
       extra="ignore",
   )

   # --- 运行环境 ---
   ENV: str = "development"
   DEBUG: bool = True

   # --- 数据库（MySQL） ---
   DB_HOST: str = "127.0.0.1"
   DB_PORT: int = 3306
   DB_USER: str = "root"
   DB_PASSWORD: str = ""
   DB_DATABASE: str = "copymind"

   @property
   def DATABASE_URL(self) -> str:
       return (
           f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
           f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"
           "?charset=utf8mb4"
       )

   # --- AI API ---
   AI_API_KEY: str = ""
   AI_API_BASE: str = "https://api.deepseek.com/v1"
   AI_MODEL: str = "deepseek-chat"

   # --- Redis（可选） ---
   REDIS_URL: str = ""

   # --- 日志 ---
   LOG_LEVEL: str = "DEBUG"
   LOG_FILE: str = "logs/copymind.log"

   # --- CORS ---
   CORS_ORIGINS: str = '["*"]'

   @property
   def cors_origins_list(self) -> list[str]:
       return json.loads(self.CORS_ORIGINS)

   # --- 限流 ---

   # --- 用户日分析次数限制 ---
   DAILY_LIMIT_NORMAL: int = 5
   DAILY_LIMIT_FREQUENT: int = 20
   DAILY_LIMIT_VIP: int = 100

   # --- 定时任务 ---
   DAILY_STATS_SCHEDULE_HOUR: int = 3
   DAILY_STATS_SCHEDULE_MINUTE: int = 0
   RATE_LIMIT_PER_MINUTE: int = 60


settings = Settings()


# 项目根路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
