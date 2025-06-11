"""
Конфигурационный модуль для бота.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import os
from pathlib import Path

class Config(BaseModel):
    """Класс конфигурации бота."""
    # Telegram settings
    TELEGRAM_BOT_TOKEN: str = Field(..., min_length=1)
    TELEGRAM_ADMIN_IDS: List[int] = Field(default_factory=list)
    TELEGRAM_CHANNEL_ID: str = Field(..., min_length=1)
    
    # Database settings
    DB_PATH: str = Field(default="data/bot.db")
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LOG_FILE: str = Field(default="bot.log")
    LOGS_DIR: str = Field(default="logs")
    
    # MLflow settings
    MLFLOW_TRACKING_URI: str = Field(default="http://localhost:5000")
    EXPERIMENT_NAME: str = Field(default="telegram_bot")
    
    # Kaggle settings
    KAGGLE_USERNAME: str = Field(..., min_length=1)
    KAGGLE_KEY: str = Field(..., min_length=1)
    COMPETITION_ID: Optional[str] = Field(default=None)
    
    # File settings
    NOTEBOOKS_DIR: str = Field(default="notebooks")
    MAX_IMAGE_SIZE: int = Field(default=5 * 1024 * 1024)  # 5MB
    IMAGE_QUALITY: int = Field(default=85)
    
    # Retry settings
    MAX_RETRIES: int = Field(default=3)
    RETRY_DELAY: int = Field(default=5)
    
    # Post timing settings
    MORNING_POST_TIME: str = Field(default="09:00")
    EVENING_POST_TIME: str = Field(default="21:00")
    
    # Voting settings
    MAX_VOTES_PER_USER: int = Field(default=3)
    VOTE_COOLDOWN: int = Field(default=24)
    
    # Learning settings
    MIN_LEARNING_TIME: int = Field(default=30)
    MAX_LEARNING_TIME: int = Field(default=240)
    
    # Environment
    ENV: str = Field(default="development")

    @field_validator('TELEGRAM_BOT_TOKEN')
    @classmethod
    def validate_token(cls, v: str) -> str:
        if not v:
            raise ValueError("Token cannot be empty")
        return v

    @field_validator('TELEGRAM_ADMIN_IDS')
    @classmethod
    def validate_admin_ids(cls, v: List[int]) -> List[int]:
        if not v:
            raise ValueError("At least one admin ID must be provided")
        return v

    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v

    @field_validator('MORNING_POST_TIME', 'EVENING_POST_TIME')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        try:
            hours, minutes = map(int, v.split(':'))
            if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                raise ValueError
        except ValueError as e:
            raise ValueError("Time must be in format HH:MM") from e
        return v

# Глобальный экземпляр конфигурации
_config = None

def get_config() -> Config:
    """Получение экземпляра конфигурации (Singleton)."""
    global _config
    if _config is None:
        _config = Config(
            TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN"),
            TELEGRAM_ADMIN_IDS=[int(id) for id in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if id],
            TELEGRAM_CHANNEL_ID=os.getenv("TELEGRAM_CHANNEL_ID"),
            KAGGLE_USERNAME=os.getenv("KAGGLE_USERNAME"),
            KAGGLE_KEY=os.getenv("KAGGLE_KEY"),
            DB_PATH=os.getenv("DB_PATH", "data/bot.db"),
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
            LOG_FILE=os.getenv("LOG_FILE", "bot.log"),
            LOGS_DIR=os.getenv("LOGS_DIR", "logs"),
            MLFLOW_TRACKING_URI=os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"),
            EXPERIMENT_NAME=os.getenv("EXPERIMENT_NAME", "telegram_bot"),
            NOTEBOOKS_DIR=os.getenv("NOTEBOOKS_DIR", "notebooks"),
            MAX_IMAGE_SIZE=int(os.getenv("MAX_IMAGE_SIZE", "5242880")),
            IMAGE_QUALITY=int(os.getenv("IMAGE_QUALITY", "85")),
            MAX_RETRIES=int(os.getenv("MAX_RETRIES", "3")),
            RETRY_DELAY=int(os.getenv("RETRY_DELAY", "5")),
            MORNING_POST_TIME=os.getenv("MORNING_POST_TIME", "09:00"),
            EVENING_POST_TIME=os.getenv("EVENING_POST_TIME", "21:00"),
            MAX_VOTES_PER_USER=int(os.getenv("MAX_VOTES_PER_USER", "3")),
            VOTE_COOLDOWN=int(os.getenv("VOTE_COOLDOWN", "24")),
            MIN_LEARNING_TIME=int(os.getenv("MIN_LEARNING_TIME", "30")),
            MAX_LEARNING_TIME=int(os.getenv("MAX_LEARNING_TIME", "240")),
            ENV=os.getenv("ENV", "development")
        )
    return _config 


