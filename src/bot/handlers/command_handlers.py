"""
Модуль с обработчиками команд бота.
"""
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler
from typing import Dict, Any, Optional
from src.utils.logger import setup_logger

from src.ui.messages.message_manager import MessageManager
from src.ui.keyboards.keyboard_manager import KeyboardManager
from src.core.moderation.vote_manager import VoteManager
from src.utils.database.db_manager import DatabaseManager
from src.core.competition.competition_manager import CompetitionManager
from src.core.learning.notebook_parser import NotebookParser

logger = setup_logger(__name__)

class CommandHandlers:
    """Обработчики команд бота."""

    def __init__(self, db_manager: DatabaseManager,
                 message_manager: MessageManager,
                 keyboard_manager: KeyboardManager,
                 vote_manager: VoteManager,
                 competition_manager: CompetitionManager,
                 notebook_parser: NotebookParser):
        """Инициализация обработчиков команд."""
        self.db_manager = db_manager
        self.message_manager = message_manager
        self.keyboard_manager = keyboard_manager
        self.vote_manager = vote_manager
        self.competition_manager = competition_manager
        self.notebook_parser = notebook_parser

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /start."""
        try:
            user = update.effective_user
            if not user:
                logger.error("Не удалось получить информацию о пользователе")
                return

            # Добавляем пользователя в базу данных
            await self.db_manager.add_user(
                user_id=user.id,
                username=user.username or "",
                first_name=user.first_name or "",
                last_name=user.last_name or ""
            )

            # Получаем приветственное сообщение
            welcome_message = self.message_manager.get_welcome_message(
                username=user.first_name or user.username or "Пользователь"
            )
            
            # Отправляем сообщение
            await update.message.reply_text(
                text=welcome_message,
                reply_markup=self.keyboard_manager.get_main_menu()
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике start: {e}")
            await update.message.reply_text(
                "Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже."
            )

    async def vote(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /vote."""
        try:
            user = update.effective_user
            if not user:
                logger.error("Не удалось получить информацию о пользователе")
                return

            # Получаем текущую тему для голосования
            topic = await self.vote_manager.get_current_topic()
            if not topic:
                await update.message.reply_text(
                    "В данный момент нет активных тем для голосования."
                )
                return

            # Получаем статистику голосования
            total_votes = await self.vote_manager.get_topic_votes(topic['id'])
            user_votes = await self.vote_manager.get_user_votes(user.id, topic['id'])

            # Формируем сообщение
            vote_message = self.message_manager.get_vote_message(
                topic=topic['title'],
                total_votes=total_votes,
                user_votes=user_votes
            )

            # Отправляем сообщение с клавиатурой для голосования
            await update.message.reply_text(
                text=vote_message,
                reply_markup=self.keyboard_manager.get_vote_keyboard(topic['id'])
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике vote: {e}")
            await update.message.reply_text(
                "Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже."
            )

    async def plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /plan."""
        try:
            user = update.effective_user
            if not user:
                logger.error("Не удалось получить информацию о пользователе")
                return

            # Получаем план пользователя
            plan = await self.db_manager.get_user_plan(user.id)
            if not plan:
                await update.message.reply_text(
                    "У вас пока нет плана обучения. Используйте команду /start для начала работы."
                )
                return

            # Формируем сообщение с планом
            plan_message = self.message_manager.get_plan_message(plan)
            
            # Отправляем сообщение
            await update.message.reply_text(
                text=plan_message,
                reply_markup=self.keyboard_manager.get_plan_keyboard()
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике plan: {e}")
            await update.message.reply_text(
                "Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже."
            )

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /stats."""
        try:
            user = update.effective_user
            if not user:
                logger.error("Не удалось получить информацию о пользователе")
                return

            # Получаем статистику пользователя
            stats = await self.db_manager.get_user_stats(user.id)
            if not stats:
                await update.message.reply_text(
                    "Статистика пока недоступна. Начните обучение, чтобы увидеть свой прогресс."
                )
                return

            # Формируем сообщение со статистикой
            stats_message = self.message_manager.get_stats_message(stats)
            
            # Отправляем сообщение
            await update.message.reply_text(
                text=stats_message,
                reply_markup=self.keyboard_manager.get_stats_keyboard()
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике stats: {e}")
            await update.message.reply_text(
                "Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже."
            )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /help."""
        try:
            help_message = self.message_manager.get_help_message()
            await update.message.reply_text(
                text=help_message,
                reply_markup=self.keyboard_manager.get_help_keyboard()
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике help: {e}")
            await update.message.reply_text(
                "Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже."
            )

    async def competition(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /competition."""
        try:
            user = update.effective_user
            if not user:
                logger.error("Не удалось получить информацию о пользователе")
                return

            # Получаем информацию о текущем соревновании
            competition = await self.competition_manager.get_current_competition()
            if not competition:
                await update.message.reply_text(
                    "В данный момент нет активных соревнований."
                )
                return

            # Формируем сообщение о соревновании
            competition_message = self.message_manager.get_competition_message(competition)
            
            # Отправляем сообщение
            await update.message.reply_text(
                text=competition_message,
                reply_markup=self.keyboard_manager.get_competition_keyboard(competition['id'])
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике competition: {e}")
            await update.message.reply_text(
                "Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже."
            )

def setup_command_handlers(
    application: Application,
    db_manager: DatabaseManager,
    notebook_parser: NotebookParser,
    competition_manager: CompetitionManager,
    vote_manager: VoteManager,
    message_manager: MessageManager,
    keyboard_manager: KeyboardManager
) -> None:
    """Настройка обработчиков команд."""
    handlers = CommandHandlers(
        db_manager=db_manager,
        message_manager=message_manager,
        keyboard_manager=keyboard_manager,
        vote_manager=vote_manager,
        competition_manager=competition_manager,
        notebook_parser=notebook_parser
    )
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("help", handlers.help))
    application.add_handler(CommandHandler("vote", handlers.vote))
    application.add_handler(CommandHandler("plan", handlers.plan))
    application.add_handler(CommandHandler("stats", handlers.stats))
    application.add_handler(CommandHandler("competition", handlers.competition)) 