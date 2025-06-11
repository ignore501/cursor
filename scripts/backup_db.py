#!/usr/bin/env python3
"""
Скрипт для автоматического создания бэкапов базы данных.
Создает бэкап с временной меткой и удаляет старые бэкапы.
"""

import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
import argparse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_directories():
    """Создает необходимые директории, если они не существуют."""
    Path('backups').mkdir(exist_ok=True)
    Path('logs').mkdir(exist_ok=True)

def create_backup(db_path: str, max_backups: int = 3):
    """
    Создает бэкап базы данных и удаляет старые бэкапы.
    
    Args:
        db_path: Путь к файлу базы данных
        max_backups: Максимальное количество хранимых бэкапов
    """
    try:
        # Создаем имя файла бэкапа с временной меткой
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_name = f'bot.db.backup.{timestamp}'
        backup_path = os.path.join('backups', backup_name)
        
        # Создаем бэкап
        logger.info(f'Создание бэкапа {backup_name}...')
        shutil.copy2(db_path, backup_path)
        logger.info(f'Бэкап успешно создан: {backup_path}')
        
        # Получаем список всех бэкапов
        backups = sorted(
            [f for f in os.listdir('backups') if f.startswith('bot.db.backup.')],
            reverse=True
        )
        
        # Удаляем старые бэкапы
        if len(backups) > max_backups:
            for old_backup in backups[max_backups:]:
                old_backup_path = os.path.join('backups', old_backup)
                os.remove(old_backup_path)
                logger.info(f'Удален старый бэкап: {old_backup}')
        
        logger.info(f'Текущее количество бэкапов: {len(backups)}')
        
    except Exception as e:
        logger.error(f'Ошибка при создании бэкапа: {str(e)}')
        raise

def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description='Создание бэкапа базы данных')
    parser.add_argument(
        '--db-path',
        default='bot.db',
        help='Путь к файлу базы данных (по умолчанию: bot.db)'
    )
    parser.add_argument(
        '--max-backups',
        type=int,
        default=5,
        help='Максимальное количество хранимых бэкапов (по умолчанию: 5)'
    )
    
    args = parser.parse_args()
    
    try:
        setup_directories()
        create_backup(args.db_path, args.max_backups)
    except Exception as e:
        logger.error(f'Критическая ошибка: {str(e)}')
        exit(1)

if __name__ == '__main__':
    main() 