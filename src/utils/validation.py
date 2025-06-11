"""
Модуль с функциями валидации.
"""
import re
from typing import List

def validate_email(email: str) -> bool:
    """
    Проверка корректности email адреса.
    
    Args:
        email (str): Email адрес для проверки
        
    Returns:
        bool: True если email корректен, False в противном случае
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Проверка корректности номера телефона.
    
    Args:
        phone (str): Номер телефона для проверки
        
    Returns:
        bool: True если номер корректен, False в противном случае
    """
    # Удаляем все нецифровые символы
    digits = re.sub(r'\D', '', phone)
    # Проверяем длину и формат
    return len(digits) >= 10 and len(digits) <= 15

def is_valid_url(url: str) -> bool:
    """
    Проверка корректности URL.
    
    Args:
        url (str): URL для проверки
        
    Returns:
        bool: True если URL корректен, False в противном случае
    """
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(pattern, url))

def is_valid_file_type(file_path: str, allowed_extensions: List[str]) -> bool:
    """
    Проверка типа файла.
    
    Args:
        file_path (str): Путь к файлу
        allowed_extensions (List[str]): Список разрешенных расширений
        
    Returns:
        bool: True если тип файла разрешен, False в противном случае
    """
    extension = file_path.lower().split('.')[-1]
    return extension in allowed_extensions 