"""
Скрипт для сброса и пересоздания базы данных.
Используйте с осторожностью - все данные будут удалены!
"""
import asyncio
import os
import sys
from pathlib import Path
import shutil
from datetime import datetime

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.database.db_manager import DatabaseManager
from src.config.config import get_config
from src.utils.logger import setup_logger

# Инициализация логгера
logger = setup_logger("db_reset")

async def reset_database():
    """Сброс и пересоздание базы данных"""
    db_path = os.getenv('DB_PATH', 'data/bot.db')
    
    # Создаем резервную копию
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(db_path, backup_path)
        logger.info(f"Создана резервная копия: {backup_path}")
        
        # Удаляем существующую базу
        os.remove(db_path)
        logger.info(f"Удалена существующая база данных: {db_path}")
    
    # Инициализируем новую базу
    db_manager = DatabaseManager(db_path)
    await db_manager.initialize()
    logger.info("База данных успешно пересоздана")
    
    # Добавляем тестовые данные, если требуется
    if os.getenv('ADD_TEST_DATA', '').lower() == 'true':
        await add_test_data(db_manager)
        logger.info("Добавлены тестовые данные")

async def add_test_data(db_manager):
    """Добавление тестовых данных"""
    async with db_manager.get_connection() as conn:
        # Добавляем тестового пользователя
        await conn.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, created_at, last_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (123456789, 'test_user', 'Test', 'User', datetime.now(), datetime.now()))
        
        # Добавляем тестовое соревнование
        await conn.execute('''
            INSERT INTO competitions (competition_id, title, description, start_date, end_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('test_comp', 'Test Competition', 'Test Description', datetime.now(), datetime.now(), datetime.now()))
        
        # Добавляем тестовую тему
        await conn.execute('''
            INSERT INTO topics (title, description, competition_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Test Topic', 'Test Description', 'test_comp', datetime.now(), datetime.now()))
        
        await conn.commit()

if __name__ == "__main__":
    if input("ВНИМАНИЕ: Это действие удалит все данные из базы данных. Продолжить? (y/N): ").lower() == 'y':
        asyncio.run(reset_database())
    else:
        logger.info("Операция отменена") 