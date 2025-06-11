"""
Модуль с функциями для работы с файлами.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Создание директории, если она не существует.
    
    Args:
        path (Union[str, Path]): Путь к директории
        
    Returns:
        Path: Путь к созданной директории
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def sanitize_filename(filename: str) -> str:
    """
    Очистка имени файла от недопустимых символов.
    
    Args:
        filename (str): Исходное имя файла
        
    Returns:
        str: Очищенное имя файла
    """
    # Заменяем недопустимые символы на подчеркивание
    sanitized = filename.replace('\\', '_').replace('/', '_').replace(':', '_')
    sanitized = sanitized.replace('*', '_').replace('?', '_').replace('"', '_')
    sanitized = sanitized.replace('<', '_').replace('>', '_').replace('|', '_')
    
    # Удаляем начальные и конечные пробелы и точки
    sanitized = sanitized.strip('. ')
    
    return sanitized

def load_json(file_path: str) -> Dict[str, Any]:
    """
    Загрузка данных из JSON файла.
    
    Args:
        file_path (str): Путь к файлу
        
    Returns:
        Dict[str, Any]: Загруженные данные
        
    Raises:
        FileNotFoundError: Если файл не найден
        json.JSONDecodeError: Если файл содержит некорректный JSON
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: Dict[str, Any], file_path: str) -> bool:
    """
    Сохранение данных в JSON файл.
    
    Args:
        data (Dict[str, Any]): Данные для сохранения
        file_path (str): Путь к файлу
        
    Returns:
        bool: True если сохранение успешно, False в противном случае
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def get_file_extension(file_path: str) -> str:
    """
    Получение расширения файла.
    
    Args:
        file_path (str): Путь к файлу
        
    Returns:
        str: Расширение файла (в нижнем регистре)
    """
    return os.path.splitext(file_path)[1].lower()

def get_file_info(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Получение информации о файле.
    
    Args:
        file_path (str): Путь к файлу
        
    Returns:
        Optional[Dict[str, Any]]: Информация о файле или None если файл не существует
    """
    try:
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'extension': get_file_extension(file_path)
        }
    except OSError:
        return None 