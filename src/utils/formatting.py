"""
Модуль с функциями форматирования.
"""
from typing import Any, Union
from datetime import datetime

def truncate_message(text: str, max_length: int = 4096) -> str:
    """
    Обрезает сообщение до максимальной длины.
    
    Args:
        text (str): Исходный текст
        max_length (int): Максимальная длина сообщения
        
    Returns:
        str: Обрезанный текст
    """
    if not text:
        return ""
    if max_length <= 0:
        return "..."
    if len(text) <= max_length:
        return text
    return "." * max_length if max_length <= 3 else f"{text[:max_length - 3]}..."

def format_message(text: str, **kwargs: Any) -> str:
    """
    Форматирование сообщения с подстановкой переменных.
    
    Args:
        text (str): Текст с плейсхолдерами
        **kwargs: Переменные для подстановки
        
    Returns:
        str: Отформатированный текст
    """
    return text.format(**kwargs)

def format_date(date: Union[str, datetime]) -> str:
    """
    Форматирование даты в строку.

    Args:
        date (Union[str, datetime]): Дата в виде строки или объекта datetime

    Returns:
        str: Отформатированная дата
    """
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")
    return date.strftime("%d.%m.%Y")

def format_time(dt: Union[str, datetime], fmt: str = "%H:%M") -> str:
    """
    Форматирует время в указанный формат.
    
    Args:
        dt (Union[str, datetime]): Время для форматирования
        fmt (str): Формат вывода
        
    Returns:
        str: Отформатированное время
    """
    if isinstance(dt, str):
        dt = datetime.strptime(dt, "%H:%M:%S")
    return dt.strftime(fmt)

def format_number(number: Union[int, float], sep: str = " ") -> str:
    """
    Форматирует число с разделителем разрядов.
    
    Args:
        number (Union[int, float]): Число для форматирования
        sep (str): Разделитель разрядов
        
    Returns:
        str: Отформатированное число
    """
    return f"{number:,}".replace(",", sep)

def format_percentage(value: float, precision: int = 2) -> str:
    """
    Форматирует число как процент с указанной точностью.
    
    Args:
        value (float): Значение для форматирования
        precision (int): Количество знаков после запятой
        
    Returns:
        str: Отформатированный процент
    """
    return f"{value * 100:.{precision}f}%"

def format_size(size_bytes: int) -> str:
    """
    Форматирует размер в байтах в человекочитаемый формат.
    
    Args:
        size_bytes (int): Размер в байтах
        
    Returns:
        str: Отформатированный размер
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB" 