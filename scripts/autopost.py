"""
Основной модуль Telegram бота для автоматизации постов о прогрессе обучения.
"""
import logging
from datetime import datetime, time
from pathlib import Path
from typing import Dict, List, Optional

import mlflow
import pandas as pd
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import (
    CHANNEL_ID,
    DATA_DIR,
    EXPERIMENT_NAME,
    LOG_FORMAT,
    LOG_LEVEL,
    LOG_FILE,
    MLFLOW_TRACKING_URI,
    TELEGRAM_BOT_TOKEN,
)
from scripts.database import Database
from scripts.jupyter_parser import JupyterParser
from scripts.moderator import Moderator
from scripts.post_templates import PostGenerator

# Настройка логирования
logging.basicConfig(
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Инициализация MLflow
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

class KaggleLearningBot:
    """Основной класс бота для автоматизации постов."""

    def __init__(self):
        """Инициализация бота и необходимых компонентов."""
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.post_generator = PostGenerator(DATA_DIR)
        self.jupyter_parser = JupyterParser()
        self.moderator = Moderator()
        self.db = Database()
        
        # Регистрация обработчиков команд
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("vote_topic", self.vote_topic))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.user_stats))
        self.application.add_handler(CommandHandler("unblock", self.unblock_user))
        self.application.add_handler(CommandHandler("topics", self.list_topics))
        self.application.add_handler(CommandHandler("vote", self.vote_for_topic))
        
        # Обработчик всех сообщений для модерации
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.moderate_message)
        )
        
        # Планировщик постов
        self.application.job_queue.run_daily(
            self.morning_post,
            time=time(hour=9, minute=0),
            name="morning_post",
        )
        self.application.job_queue.run_daily(
            self.evening_post,
            time=time(hour=20, minute=0),
            name="evening_post",
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /start."""
        user = update.message.from_user
        self.db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        await update.message.reply_text(
            "Привет! Я бот для автоматизации постов о прогрессе обучения Data Science. "
            "Используйте /help для получения списка доступных команд."
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /help."""
        help_text = """
Доступные команды:
/start - Начать работу с ботом
/help - Показать это сообщение
/vote_topic <тема> - Предложить тему для изучения
/vote <id> - Проголосовать за тему
/topics - Показать список тем для голосования
/stats <id> - Показать статистику пользователя
/unblock <id> - Разблокировать пользователя
        """
        await update.message.reply_text(help_text)

    async def vote_topic(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /vote_topic."""
        if not context.args:
            await update.message.reply_text(
                "Пожалуйста, укажите тему для голосования. "
                "Пример: /vote_topic Feature Engineering"
            )
            return

        topic = " ".join(context.args)
        topic_id = self.db.add_voting_topic(topic, update.message.from_user.id)
        
        await update.message.reply_text(
            f"Тема '{topic}' добавлена для голосования! "
            f"ID темы: {topic_id}\n"
            f"Используйте /vote {topic_id} для голосования."
        )

    async def vote_for_topic(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /vote."""
        if not context.args:
            await update.message.reply_text(
                "Пожалуйста, укажите ID темы. Пример: /vote 1"
            )
            return
            
        try:
            topic_id = int(context.args[0])
            self.db.vote_for_topic(topic_id)
            await update.message.reply_text(f"Ваш голос за тему {topic_id} учтен!")
        except ValueError:
            await update.message.reply_text("Неверный формат ID темы")

    async def list_topics(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /topics."""
        topics = self.db.get_voting_topics(limit=10)
        
        if not topics:
            await update.message.reply_text("Нет доступных тем для голосования")
            return
            
        message = "Темы для голосования:\n\n"
        for topic_id, topic, votes, created_at in topics:
            message += f"ID: {topic_id}\n"
            message += f"Тема: {topic}\n"
            message += f"Голосов: {votes}\n"
            message += f"Добавлена: {created_at}\n\n"
            
        await update.message.reply_text(message)

    async def morning_post(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Генерация и публикация утреннего поста."""
        try:
            post = self.post_generator.generate_morning_post()
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=post,
                parse_mode="Markdown"
            )
            logger.info("Утренний пост успешно опубликован")
        except Exception as e:
            logger.error(f"Ошибка при публикации утреннего поста: {e}")

    async def evening_post(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Генерация и публикация вечернего поста."""
        try:
            # Получение метрик из MLflow
            metrics = self.get_today_metrics()
            
            # Генерация поста
            post = self.post_generator.generate_evening_post(metrics)
            
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=post,
                parse_mode="Markdown"
            )
            logger.info("Вечерний пост успешно опубликован")
        except Exception as e:
            logger.error(f"Ошибка при публикации вечернего поста: {e}")

    def get_today_metrics(self) -> Dict:
        """Получение метрик за сегодня из MLflow."""
        today = datetime.now().date()
        metrics = {}
        
        # Получение последнего запуска эксперимента
        runs = mlflow.search_runs(
            experiment_names=[EXPERIMENT_NAME],
            filter_string=f"start_time >= '{today}'"
        )
        
        if not runs.empty:
            latest_run = runs.iloc[0]
            metrics = {
                "accuracy": latest_run.get("metrics.accuracy", 0),
                "loss": latest_run.get("metrics.loss", 0),
                "f1": latest_run.get("metrics.f1", 0),
                "precision": latest_run.get("metrics.precision", 0),
                "recall": latest_run.get("metrics.recall", 0),
                "auc": latest_run.get("metrics.auc", 0),
                "rmse": latest_run.get("metrics.rmse", 0),
                "mae": latest_run.get("metrics.mae", 0),
                "r2": latest_run.get("metrics.r2", 0)
            }
        
        return metrics

    async def moderate_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Модерация входящих сообщений."""
        if not await self.moderator.check_message(update, context):
            return
            
        # Если сообщение прошло модерацию, можно добавить дополнительную обработку
        logger.info(f"Сообщение от {update.message.from_user.id} прошло модерацию")

    async def user_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Показать статистику пользователя."""
        if not context.args:
            await update.message.reply_text(
                "Пожалуйста, укажите ID пользователя. Пример: /stats 123456789"
            )
            return
            
        try:
            user_id = int(context.args[0])
            stats = self.db.get_user_stats(user_id)
            
            if stats:
                message = (
                    f"Статистика пользователя {user_id}:\n"
                    f"Имя: {stats['first_name']} {stats['last_name']}\n"
                    f"Username: @{stats['username']}\n"
                    f"Количество сообщений: {stats['message_count']}\n"
                    f"Предупреждения: {stats['warnings']}/3\n"
                    f"Статус: {'Заблокирован' if stats['is_blocked'] else 'Активен'}\n"
                    f"Дата регистрации: {stats['created_at']}"
                )
            else:
                message = f"Статистика для пользователя {user_id} не найдена"
                
            await update.message.reply_text(message)
        except ValueError:
            await update.message.reply_text("Неверный формат ID пользователя")

    async def unblock_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Разблокировать пользователя."""
        if not context.args:
            await update.message.reply_text(
                "Пожалуйста, укажите ID пользователя. Пример: /unblock 123456789"
            )
            return
            
        try:
            user_id = int(context.args[0])
            self.db.unblock_user(user_id)
            await update.message.reply_text(f"Пользователь {user_id} разблокирован")
        except ValueError:
            await update.message.reply_text("Неверный формат ID пользователя")

    def run(self):
        """Запуск бота."""
        logger.info("Запуск бота...")
        self.application.run_polling()

if __name__ == "__main__":
    bot = KaggleLearningBot()
    bot.run() 