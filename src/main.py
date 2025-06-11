"""
Основной модуль приложения.
"""
import asyncio
from pathlib import Path
from src.config.config import get_config
from src.utils.database.db_manager import DatabaseManager
from src.core.learning.learning_manager import LearningManager
from src.core.learning.notebook_parser import NotebookParser
from src.core.competition.competition_manager import CompetitionManager
from src.bot.bot import main as run_bot
from src.core.moderation.vote_manager import VoteManager
from src.utils.logger import setup_logger

# Инициализация логгера
logger = setup_logger(__name__)

async def initialize_managers():
    """Инициализация всех менеджеров"""
    try:
        # Получаем конфигурацию
        config = get_config()
        
        # Создаем директорию для базы данных, если она не существует
        db_path = Path(config.DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем менеджеры
        db_manager = DatabaseManager(db_path=str(db_path))
        
        # Инициализируем базу данных
        try:
            await db_manager.initialize()
            logger.info("База данных успешно инициализирована")
        except Exception as e:
            logger.error(f"Ошибка при инициализации базы данных: {e}")
            raise
        
        # Проверяем, что таблицы созданы
        try:
            async with db_manager.get_connection() as conn:
                await db_manager.check_tables(conn)
            logger.info("Таблицы базы данных проверены")
        except Exception as e:
            logger.error(f"Ошибка при проверке таблиц: {e}")
            raise
        
        learning_manager = LearningManager(db_manager)
        await learning_manager.initialize()
        
        notebook_parser = NotebookParser()
        competition_manager = CompetitionManager(db_manager)
        vote_manager = VoteManager(db_manager)
        
        return {
            "config": config,
            "db_manager": db_manager,
            "learning_manager": learning_manager,
            "notebook_parser": notebook_parser,
            "competition_manager": competition_manager,
            "vote_manager": vote_manager
        }
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации менеджеров: {e}")
        raise

async def main():
    """Основная функция запуска приложения"""
    try:
        # Инициализируем менеджеры
        managers = await initialize_managers()
        
        # Запускаем бота
        await run_bot(managers)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}")
        raise

if __name__ == "__main__":
    try:
        # Запускаем основную функцию
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}") 