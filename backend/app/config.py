"""应用配置管理"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "copymind"
    deepseek_api_key: str = ""
    deepseek_api_url: str = "https://api.deepseek.com"
    qwen_api_key: str = ""
    primary_llm: str = "deepseek"
    backup_llm: str = "qwen"
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def database_url(self) -> str:
        return f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def has_any_api_key(self) -> bool:
        return bool(self.deepseek_api_key)

settings = Settings()
