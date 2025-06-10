"""
Тесты для конфигурационного модуля (config.py).
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch

from config import (
    BASE_DIR,
    SCRIPTS_DIR,
    DATA_DIR,
    TELEGRAM_BOT_TOKEN,
    CHANNEL_ID,
    MLFLOW_TRACKING_URI,
    EXPERIMENT_NAME,
    MORNING_POST_TIME,
    EVENING_POST_TIME,
    JUPYTER_TEMPLATES_DIR,
    NOTEBOOKS_DIR,
    BART_MODEL_NAME,
    MAX_LENGTH,
    MIN_LENGTH,
    MONETIZATION_THRESHOLDS,
    LOG_FORMAT,
    LOG_LEVEL,
    LOG_FILE
)

class TestConfig:
    """Тесты для конфигурационного модуля."""

    def test_base_paths(self):
        """Проверка базовых путей."""
        assert isinstance(BASE_DIR, Path)
        assert isinstance(SCRIPTS_DIR, Path)
        assert isinstance(DATA_DIR, Path)
        assert SCRIPTS_DIR == BASE_DIR / "scripts"
        assert DATA_DIR == BASE_DIR / "data"

    def test_telegram_settings(self, mock_env_vars):
        """Проверка настроек Telegram."""
        assert TELEGRAM_BOT_TOKEN == "test_token"
        assert CHANNEL_ID == "-100123456789"

    def test_mlflow_settings(self, mock_env_vars):
        """Проверка настроек MLflow."""
        assert MLFLOW_TRACKING_URI == "http://localhost:5000"
        assert EXPERIMENT_NAME == "kaggle_learning_progress"

    def test_time_settings(self):
        """Проверка временных настроек."""
        assert MORNING_POST_TIME == "09:00"
        assert EVENING_POST_TIME == "20:00"

    def test_jupyter_settings(self):
        """Проверка настроек Jupyter."""
        assert JUPYTER_TEMPLATES_DIR == DATA_DIR / "templates"
        assert NOTEBOOKS_DIR == DATA_DIR / "notebooks"

    def test_bart_settings(self):
        """Проверка настроек BART."""
        assert BART_MODEL_NAME == "facebook/bart-large-cnn"
        assert MAX_LENGTH == 1024
        assert MIN_LENGTH == 50

    def test_monetization_thresholds(self):
        """Проверка порогов монетизации."""
        assert MONETIZATION_THRESHOLDS["PARTNER_LINKS"] == 500
        assert MONETIZATION_THRESHOLDS["NOTEBOOK_TEMPLATES"] == 1000
        assert MONETIZATION_THRESHOLDS["CONSULTATIONS"] == 3000

    def test_logging_settings(self):
        """Проверка настроек логирования."""
        assert LOG_FORMAT == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert LOG_LEVEL == "INFO"
        assert LOG_FILE == BASE_DIR / "logs" / "bot.log"

    def test_directory_creation(self, temp_dir):
        """Проверка создания директорий."""
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            # Импортируем конфиг заново для выполнения создания директорий
            import importlib
            import config
            importlib.reload(config)
            
            assert mock_mkdir.call_count >= 4  # Проверяем, что mkdir вызывался для всех директорий 