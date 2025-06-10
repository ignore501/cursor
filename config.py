"""
Конфигурационный файл проекта.
Содержит все настройки и константы.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Базовые пути
BASE_DIR = Path(__file__).parent
SCRIPTS_DIR = BASE_DIR / "scripts"
DATA_DIR = BASE_DIR / "data"

# Telegram настройки
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# MLflow настройки
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
EXPERIMENT_NAME = "kaggle_learning_progress"

# Временные настройки
MORNING_POST_TIME = "08:40"  # Время публикации утреннего поста
EVENING_POST_TIME = "20:00"  # Время публикации вечернего поста

# Настройки для парсинга Jupyter
JUPYTER_TEMPLATES_DIR = DATA_DIR / "templates"
NOTEBOOKS_DIR = DATA_DIR / "notebooks"

# Настройки для BART модели
BART_MODEL_NAME = "facebook/bart-large-cnn"
MAX_LENGTH = 1024
MIN_LENGTH = 50

# Монетизационные пороги
MONETIZATION_THRESHOLDS = {
    "PARTNER_LINKS": 500,    # Подписчиков для партнерских ссылок
    "NOTEBOOK_TEMPLATES": 1000,  # Подписчиков для продажи шаблонов
    "CONSULTATIONS": 3000    # Подписчиков для консультаций
}

# Настройки логирования
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "logs" / "bot.log"

# Создание необходимых директорий
for directory in [DATA_DIR, JUPYTER_TEMPLATES_DIR, NOTEBOOKS_DIR, BASE_DIR / "logs"]:
    directory.mkdir(parents=True, exist_ok=True) 