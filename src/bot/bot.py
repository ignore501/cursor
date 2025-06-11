"""
Модуль для работы с Telegram ботом.
"""
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from src.config.config import get_config
from src.utils.database.db_manager import DatabaseManager
from src.utils.logger import setup_logger
from src.bot.handlers.command_handlers import CommandHandlers, setup_command_handlers
from src.bot.handlers.message_handlers import setup_message_handlers
from src.core.learning.notebook_parser import NotebookParser
from src.core.competition.competition_manager import CompetitionManager
from src.ui.messages.message_manager import MessageManager
from src.ui.keyboards.keyboard_manager import KeyboardManager
from src.core.posts.post_manager import PostManager
from src.utils.mlflow_manager import MLflowManager
import asyncio

# Инициализация логгера
logger = setup_logger(__name__)

# Инициализация компонентов
config = get_config()
post_manager = PostManager()
notebook_parser = NotebookParser()
mlflow_manager = MLflowManager()

async def handle_error(update: Update, context: CallbackContext) -> None:
    """Обработчик ошибок."""
    logger.error(f"Произошла ошибка: {context.error}")
    if update and update.message:
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

async def send_morning_post(context: CallbackContext) -> None:
    """Отправка утреннего поста."""
    try:
        # Начинаем новый запуск в MLflow
        mlflow_manager.start_run(run_name="morning_post")

        # Получаем план на день
        plan = "1. Изучение новых тем\n2. Практические задания\n3. Обзор результатов"
        
        # Получаем цели
        goals = "1. Изучить новую тему\n2. Выполнить практическое задание\n3. Подготовить отчет"
        
        # Генерируем пост
        post = await post_manager.generate_morning_post(plan, goals)

        # Отправляем пост
        await context.bot.send_message(
            chat_id=config.TELEGRAM_CHANNEL_ID,
            text=post,
            parse_mode='HTML'
        )

        # Логируем метрики
        mlflow_manager.log_metrics({
            "post_sent": 1.0,
            "post_type": "morning"
        })

        # Завершаем запуск
        mlflow_manager.end_run()

        logger.info("Утренний пост успешно отправлен")
    except Exception as e:
        logger.error(f"Ошибка при отправке утреннего поста: {e}")
        mlflow_manager.end_run()

async def send_evening_post(context: CallbackContext) -> None:
    """Отправка вечернего поста."""
    try:
        # Начинаем новый запуск в MLflow
        mlflow_manager.start_run(run_name="evening_post")

        # Получаем сводку за день
        summary = await notebook_parser.get_today_summary()
        
        # Получаем достижения
        achievements = "1. Изучена новая тема\n2. Выполнено практическое задание\n3. Подготовлен отчет"
        
        # Генерируем пост
        post = await post_manager.generate_evening_post(summary, achievements)

        # Отправляем пост
        await context.bot.send_message(
            chat_id=config.TELEGRAM_CHANNEL_ID,
            text=post,
            parse_mode='HTML'
        )

        # Логируем метрики
        mlflow_manager.log_metrics({
            "post_sent": 1.0,
            "post_type": "evening"
        })

        # Завершаем запуск
        mlflow_manager.end_run()

        logger.info("Вечерний пост успешно отправлен")
    except Exception as e:
        logger.error(f"Ошибка при отправке вечернего поста: {e}")
        mlflow_manager.end_run()

async def send_reminder(context: CallbackContext) -> None:
    """Отправка напоминания."""
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Не забудьте позаниматься сегодня!"
    )

async def send_feedback_reminder(context: CallbackContext) -> None:
    """Отправка напоминания о фидбеке."""
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Пожалуйста, оставьте отзыв о вашем обучении!"
    )

async def main(managers: dict):
    """Основная функция запуска бота"""
    application = None
    try:
        # Создаем приложение
        token = managers["config"].TELEGRAM_BOT_TOKEN
        application = Application.builder().token(token).build()
        
        # Сохраняем менеджеры в данных бота
        application.bot_data.update(managers)
        
        # Создаем менеджеры сообщений и клавиатур
        message_manager = MessageManager()
        keyboard_manager = KeyboardManager()
        
        # Настраиваем обработчики команд
        setup_command_handlers(
            application,
            managers["db_manager"],
            managers["notebook_parser"],
            managers["competition_manager"],
            managers["vote_manager"],
            message_manager,
            keyboard_manager
        )
        
        # Настраиваем обработчики сообщений
        setup_message_handlers(
            application,
            managers["db_manager"],
            managers["notebook_parser"]
        )
        
        # Добавляем обработчик ошибок
        application.add_error_handler(handle_error)
        
        # Запускаем бота
        await application.initialize()
        await application.start()
        logger.info("Бот успешно запущен")
        
        # Запускаем polling в отдельной задаче
        await application.updater.start_polling()
        
        # Ждем сигнала завершения
        stop = asyncio.Event()
        await stop.wait()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise
    finally:
        if application:
            try:
                await application.updater.stop()
                await application.stop()
                await application.shutdown()
                logger.info("Бот успешно остановлен")
            except Exception as e:
                logger.error(f"Ошибка при остановке бота: {e}")

# Удаляем запуск через asyncio.run
# if __name__ == '__main__':
#     asyncio.run(main()) 