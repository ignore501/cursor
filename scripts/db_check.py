"""
Скрипт для проверки состояния базы данных.
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
logger = setup_logger("db_check")

async def check_database():
    """Проверка структуры базы данных."""
    try:
        config = get_config()
        db_manager = DatabaseManager(config.DB_PATH)

        async with db_manager.get_connection() as db:
            # Получаем список всех таблиц
            async with db.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
                tables = [row['name'] for row in await cursor.fetchall()]

            logger.info(f"Найдены таблицы: {', '.join(tables)}")

            # Проверяем структуру каждой таблицы
            for table in tables:
                logger.info(f"\nПроверка таблицы {table}:")
                async with db.execute(f"PRAGMA table_info({table})") as cursor:
                    columns = await cursor.fetchall()
                    for col in columns:
                        logger.info(f"  Колонка: {col['name']}, Тип: {col['type']}, Nullable: {not col['notnull']}, Default: {col['dflt_value']}")

                # Проверяем индексы
                async with db.execute(f"PRAGMA index_list({table})") as cursor:
                    indexes = await cursor.fetchall()
                    if indexes:
                        logger.info("  Индексы:")
                        for idx in indexes:
                            async with db.execute(f"PRAGMA index_info({idx['name']})") as cursor2:
                                index_columns = await cursor2.fetchall()
                                logger.info(f"    {idx['name']}: {', '.join(str(col['name']) for col in index_columns)}")

            # Проверяем наличие тестовых данных
            if 'competitions' in tables:
                async with db.execute("SELECT COUNT(*) FROM competitions") as cursor:
                    count = await cursor.fetchone()
                    logger.info(f"\nКоличество соревнований: {count}")

            if 'users' in tables:
                async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                    count = await cursor.fetchone()
                    logger.info(f"Количество пользователей: {count}")

            if 'topics' in tables:
                async with db.execute("SELECT COUNT(*) FROM topics") as cursor:
                    count = await cursor.fetchone()
                    logger.info(f"Количество тем: {count}")

            if 'votes' in tables:
                async with db.execute("SELECT COUNT(*) FROM votes") as cursor:
                    count = await cursor.fetchone()
                    logger.info(f"Количество голосов: {count}")

        logger.info("\nПроверка базы данных завершена успешно")

    except Exception as e:
        logger.error(f"Ошибка при проверке базы данных: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(check_database()) 