from pydantic_settings import BaseSettings
from typing import List
import os
from functools import lru_cache


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Contract Validator API"
    DEBUG: bool = False
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["docx"]
    
    # Claude AI Settings
    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0
    
    # Perplexity AI Settings
    PERPLEXITY_API_KEY: str
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    MAX_CONCURRENT_ANALYSES: int = 5
    
    # Timeouts (in seconds)
    UPLOAD_TIMEOUT: int = 30
    ANALYSIS_TIMEOUT: int = 60
    REQUEST_TIMEOUT: int = 90

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()