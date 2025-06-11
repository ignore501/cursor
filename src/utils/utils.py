"""
Модуль с общими утилитами и реэкспортами.
"""
from typing import Any, Dict, Optional
import re
import string
import random

from src.utils.logger import setup_logger
from src.utils.validation import validate_email, validate_phone, is_valid_url, is_valid_file_type
from src.utils.formatting import (
    truncate_message, format_message, format_date, format_time,
    format_number, format_percentage, format_size
)
from src.utils.file_utils import (
    ensure_dir, sanitize_filename, load_json, save_json,
    get_file_extension, get_file_info
)

# Инициализация логгера
logger = setup_logger(__name__)

def parse_command_args(args: Optional[str]) -> Dict[str, str]:
    """
    Парсинг аргументов команды.
    
    Args:
        args (Optional[str]): Строка с аргументами
        
    Returns:
        Dict[str, str]: Словарь с аргументами
    """
    if not args:
        return {}
    return dict(arg.split('=') for arg in args.split() if '=' in arg)

def generate_random_string(length: int = 10, chars: Optional[str] = None) -> str:
    """
    Генерация случайной строки.
    
    Args:
        length (int): Длина строки
        chars (Optional[str]): Набор символов для генерации
        
    Returns:
        str: Случайная строка
    """
    if chars is None:
        chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def sanitize_text(text: str) -> str:
    """
    Очистка текста от HTML-тегов и специальных символов.
    
    Args:
        text (str): Исходный текст
        
    Returns:
        str: Очищенный текст
    """
    # Удаляем HTML-теги
    text = re.sub(r'<[^>]+>', '', text)
    # Заменяем HTML-сущности
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
    text = text.replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&apos;', "'")
    return text.strip()

# Экспортируем все функции из новых модулей
__all__ = [
    # Общие утилиты
    'parse_command_args',
    'generate_random_string',
    'sanitize_text',
    
    # Функции валидации
    'validate_email',
    'validate_phone',
    'is_valid_url',
    'is_valid_file_type',
    
    # Функции форматирования
    'truncate_message',
    'format_message',
    'format_date',
    'format_time',
    'format_number',
    'format_percentage',
    'format_size',
    
    # Функции для работы с файлами
    'ensure_dir',
    'sanitize_filename',
    'load_json',
    'save_json',
    'get_file_extension',
    'get_file_info',
]