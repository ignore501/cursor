"""
Модуль для планирования постов.
"""
import logging
from datetime import datetime, time
from telegram.ext import CallbackContext
from src.config.config import get_config

logger = logging.getLogger(__name__)

class PostScheduler:
    """Класс для планирования постов."""

    def __init__(self, bot):
        """
        Инициализация планировщика постов.
        
        Args:
            bot: Экземпляр бота
        """
        self.bot = bot
        self.config = get_config()
        self._initialized = False

    async def initialize(self) -> None:
        """Инициализация планировщика."""
        if self._initialized:
            return
        try:
            # Планируем утренний пост
            morning_time = datetime.strptime(self.config.MORNING_POST_TIME, "%H:%M").time()
            self.bot.job_queue.run_daily(
                self.bot.send_morning_post,
                time=time(hour=morning_time.hour, minute=morning_time.minute),
                name="morning_post"
            )

            # Планируем вечерний пост
            evening_time = datetime.strptime(self.config.EVENING_POST_TIME, "%H:%M").time()
            self.bot.job_queue.run_daily(
                self.bot.send_evening_post,
                time=time(hour=evening_time.hour, minute=evening_time.minute),
                name="evening_post"
            )

            self._initialized = True
            logger.info("PostScheduler успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации PostScheduler: {e}")
            raise 