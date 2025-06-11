"""
Модуль для настройки логирования.
"""
import logging
import os
from pathlib import Path
from datetime import datetime

def setup_logger(name: str = None) -> logging.Logger:
    """
    Настройка логгера.
    
    Args:
        name: Имя логгера
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Форматтер для логов с текущим временем
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Хендлер для вывода в консоль
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Хендлер для вывода в файл
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / "bot.log",
            mode='a',  # Режим добавления
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Добавляем тестовую запись
        logger.info(f"Логгер {name} инициализирован")
    
    return logger

# Создаем глобальный логгер
logger = setup_logger(__name__) 