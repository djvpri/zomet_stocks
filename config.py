from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # AI Keys
    claude_api_key: str = ""
    qwen_api_key: str = ""
    deepseek_api_key: str = ""
    gemini_api_key: str = ""
    groq_api_key: str = ""
    openai_api_key: str = ""

    # AI Manager
    ai_mode: str = "fallback"
    primary_provider: str = "qwen"
    fallback_providers: str = "deepseek,claude"
    consensus_providers: str = "qwen,deepseek,claude"

    # Firebase
    firebase_credentials_path: str = "firebase-credentials.json"

    # Scheduler
    analysis_interval_minutes: int = 60
    timezone: str = "Asia/Jakarta"

    # Market
    market_open_hour: int = 9
    market_open_minute: int = 0
    market_close_hour: int = 15
    market_close_minute: int = 30
    ihsg_symbol: str = "^JKSE"

    class Config:
        env_file = ".env"

    def get_fallback_list(self) -> List[str]:
        return [p.strip() for p in self.fallback_providers.split(",") if p.strip()]

    def get_consensus_list(self) -> List[str]:
        return [p.strip() for p in self.consensus_providers.split(",") if p.strip()]


settings = Settings()
