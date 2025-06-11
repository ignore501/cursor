"""
Скрипт для просмотра содержимого базы данных.
"""
import os
import sys
from pathlib import Path
from tabulate import tabulate

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.database.db_manager import DatabaseManager
from src.config.config import get_config
from src.utils.logger import setup_logger

# Инициализация логгера
logger = setup_logger("db_view")

async def view_table_data(db, table_name: str):
    """Просмотр данных в таблице."""
    try:
        # Получаем названия колонок
        async with db.execute(f"PRAGMA table_info({table_name})") as cursor:
            columns = [row[1] for row in await cursor.fetchall()]
        
        # Получаем данные
        async with db.execute(f"SELECT * FROM {table_name}") as cursor:
            rows = await cursor.fetchall()
        
        if rows:
            print(f"\nТаблица {table_name}:")
            print(tabulate(rows, headers=columns, tablefmt="grid"))
            print(f"Всего записей: {len(rows)}")
        else:
            print(f"\nТаблица {table_name} пуста")
            
    except Exception as e:
        logger.error(f"Ошибка при просмотре таблицы {table_name}: {e}")

async def view_database():
    """Просмотр содержимого базы данных."""
    try:
        config = get_config()
        db_manager = DatabaseManager(config.DB_PATH)
        
        async with db_manager.get_connection() as db:
            # Получаем список всех таблиц
            async with db.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
                tables = [row[0] for row in await cursor.fetchall()]
            
            # Просматриваем каждую таблицу
            for table in tables:
                if table != 'sqlite_sequence':  # Пропускаем системную таблицу
                    await view_table_data(db, table)
        
        logger.info("\nПросмотр базы данных завершен")
        
    except Exception as e:
        logger.error(f"Ошибка при просмотре базы данных: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(view_database()) 