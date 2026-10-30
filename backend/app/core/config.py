import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "SmartJobMatch AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "smartjobmatch-ai-super-secret-key-at-least-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_URL: str = "sqlite:///./smartjobmatch.db"

    # Scheduling
    SYNC_SCHEDULE_HOURS: int = 6
    ENABLE_SCHEDULED_SYNC: bool = True

    # Integrations
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_API_TOKEN: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GREENHOUSE_BOARD_TOKEN: Optional[str] = None
    LEVER_SITE_NAME: Optional[str] = None

    # Defaults
    DEFAULT_SEARCH_LOCATION: str = "Bengaluru, Karnataka, India"
    DEFAULT_MIN_MATCH_SCORE: float = 70.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

