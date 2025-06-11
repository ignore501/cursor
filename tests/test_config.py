"""
Тесты для конфигурационного модуля (config.py).
"""
import pytest
from src.config.config import Config, get_config

def test_config_loading_and_validation():
    """Тест загрузки и валидации конфигурации."""
    config = Config(
        TELEGRAM_TOKEN="test_token",
        telegram_admin_ids=[123, 456],
        telegram_channel_id="test_channel",
        kaggle_username="test_user",
        kaggle_key="test_key",
        competition_id="test_competition",
        telegram_bot_token="test_bot_token"
    )
    
    # Проверяем основные параметры
    assert config.TELEGRAM_TOKEN == "test_token"
    assert config.telegram_admin_ids == [123, 456]
    assert config.telegram_channel_id == "test_channel"
    assert config.kaggle_username == "test_user"
    assert config.kaggle_key == "test_key"
    assert config.competition_id == "test_competition"
    assert config.telegram_bot_token == "test_bot_token"
    
    # Проверяем значения по умолчанию
    assert config.DB_PATH == "bot.db"
    assert config.log_level == "INFO"
    assert config.log_format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    assert config.log_file == "bot.log"
    assert config.mlflow_tracking_uri == "http://localhost:5000"
    assert config.experiment_name == "telegram_bot"
    assert config.NOTEBOOKS_DIR == "notebooks"
    assert config.LOGS_DIR == "logs"
    assert config.env == "development"
    assert config.max_image_size == 5 * 1024 * 1024
    assert config.image_quality == 85
    assert config.max_retries == 3
    assert config.retry_delay == 5
    assert config.MORNING_POST_TIME == "09:00"
    assert config.EVENING_POST_TIME == "21:00"
    assert config.MAX_VOTES_PER_USER == 3
    assert config.VOTE_COOLDOWN == 24
    assert config.MIN_LEARNING_TIME == 30
    assert config.MAX_LEARNING_TIME == 240

def test_config_singleton():
    """Тест паттерна Singleton."""
    config1 = get_config()
    config2 = get_config()
    
    assert config1 is config2
    assert config1.TELEGRAM_TOKEN == "test_token"
    assert config1.telegram_admin_ids == [123, 456]

def test_invalid_config():
    """Тест обработки некорректной конфигурации."""
    with pytest.raises(ValueError):
        Config(
            telegram_admin_ids=[123]  # Отсутствуют обязательные поля
        ) 