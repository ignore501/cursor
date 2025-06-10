"""
Конфигурационный файл проекта.
Содержит все настройки и константы.
"""
import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

def validate_env_vars() -> None:
    """Проверяет наличие и валидность необходимых переменных окружения."""
    required_vars = ["TELEGRAM_BOT_TOKEN", "CHANNEL_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")

# Базовые пути
BASE_DIR: Path = Path(__file__).parent
SCRIPTS_DIR: Path = BASE_DIR / "scripts"
DATA_DIR: Path = BASE_DIR / "data"

# Telegram настройки
TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID: Optional[str] = os.getenv("CHANNEL_ID")

# MLflow настройки
MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
EXPERIMENT_NAME: str = "kaggle_learning_progress"

# Временные настройки
MORNING_POST_TIME = "08:40"  # Время публикации утреннего поста
EVENING_POST_TIME = "20:00"  # Время публикации вечернего поста
>>>>>>> 8f11f0a853d86a34c6147d2fcc7fd110ebbd6ee8

# Настройки для парсинга Jupyter
JUPYTER_TEMPLATES_DIR: Path = DATA_DIR / "templates"
NOTEBOOKS_DIR: Path = DATA_DIR / "notebooks"

# Настройки для BART модели
BART_MODEL_NAME: str = "facebook/bart-large-cnn"
MAX_LENGTH: int = 1024
MIN_LENGTH: int = 50

# Монетизационные пороги
MONETIZATION_THRESHOLDS: Dict[str, int] = {
    "PARTNER_LINKS": 500,    # Подписчиков для партнерских ссылок
    "NOTEBOOK_TEMPLATES": 1000,  # Подписчиков для продажи шаблонов
    "CONSULTATIONS": 3000    # Подписчиков для консультаций
}

# Настройки логирования
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL: str = "INFO"
LOG_FILE: Path = BASE_DIR / "logs" / "bot.log"

# Настройки Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")
REDIS_POOL_SIZE = int(os.getenv("REDIS_POOL_SIZE", "10"))
REDIS_TIMEOUT = int(os.getenv("REDIS_TIMEOUT", "5"))

# Настройки мониторинга
PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "9090"))
METRICS_ENABLED = os.getenv("METRICS_ENABLED", "true").lower() == "true"

# Настройки rate limiting
RATE_LIMIT_CALLS = int(os.getenv("RATE_LIMIT_CALLS", "5"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))

# Настройки кеширования
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", "3600"))

# Создание необходимых директорий
for directory in [DATA_DIR, JUPYTER_TEMPLATES_DIR, NOTEBOOKS_DIR, BASE_DIR / "logs"]:
    directory.mkdir(parents=True, exist_ok=True)

# Валидация переменных окружения при импорте
validate_env_vars() 