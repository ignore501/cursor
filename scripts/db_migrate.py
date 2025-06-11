"""
Скрипт для миграции базы данных.
Поддерживает как обновление схемы, так и перенос данных.
"""
import asyncio
import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.database.db_manager import DatabaseManager
from src.config.config import get_config
from src.utils.logger import setup_logger

# Инициализация логгера
logger = setup_logger("db_migrate")

async def backup_database(db_path: str) -> str:
    """Создание резервной копии базы данных."""
    backup_path = f"{db_path}.backup"
    try:
        if os.path.exists(db_path):
            import shutil
            shutil.copy2(db_path, backup_path)
            logger.info(f"Создана резервная копия: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Ошибка при создании резервной копии: {e}")
        raise

async def migrate_database():
    """Миграция базы данных"""
    try:
        # Получаем конфигурацию
        config = get_config()
        
        # Создаем менеджер базы данных
        db_manager = DatabaseManager(config.DB_PATH)
        
        # Подключаемся к базе данных
        async with db_manager.get_connection() as conn:
            # Получаем список существующих таблиц
            async with conn.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
                existing_tables = [row['name'] for row in await cursor.fetchall()]
            
            # Создаем новые таблицы
            await db_manager._create_tables(conn)
            
            # Если таблица topics существует, добавляем поле status
            if 'topics' in existing_tables:
                try:
                    await conn.execute("ALTER TABLE topics ADD COLUMN status TEXT DEFAULT 'active'")
                    logger.info("Добавлено поле status в таблицу topics")
                except Exception as e:
                    if "duplicate column name" not in str(e):
                        raise
                    logger.info("Поле status уже существует в таблице topics")
            
            # Если таблица users существует, добавляем поле is_blocked
            if 'users' in existing_tables:
                try:
                    await conn.execute("ALTER TABLE users ADD COLUMN is_blocked BOOLEAN DEFAULT FALSE")
                    logger.info("Добавлено поле is_blocked в таблицу users")
                except Exception as e:
                    if "duplicate column name" not in str(e):
                        raise
                    logger.info("Поле is_blocked уже существует в таблице users")
            
            await conn.commit()
            logger.info("Миграция базы данных успешно завершена")
            
    except Exception as e:
        logger.error(f"Ошибка при миграции базы данных: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(migrate_database())
    except KeyboardInterrupt:
        logger.info("Миграция прервана пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}") 