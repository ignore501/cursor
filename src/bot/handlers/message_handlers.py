from telegram.ext import Application, MessageHandler, filters, CallbackContext
from telegram import Update
from src.utils.database.db_manager import DatabaseManager
from src.core.learning.notebook_parser import NotebookParser
import logging

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Обработчик текстовых сообщений"""
    try:
        # Получаем менеджеры из данных бота
        db_manager: DatabaseManager = context.bot_data['db_manager']
        notebook_parser: NotebookParser = context.bot_data['notebook_parser']
        
        # Сохраняем сообщение в базе данных
        user_id = update.effective_user.id
        content = update.message.text
        
        async with db_manager.get_connection() as conn:
            await db_manager.save_message(conn, user_id, content)
        
        # Отправляем подтверждение
        await update.message.reply_text("Сообщение сохранено!")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text(
            "Произошла ошибка при обработке сообщения. Пожалуйста, попробуйте позже."
        )

def setup_message_handlers(
    application: Application,
    db_manager: DatabaseManager,
    notebook_parser: NotebookParser
) -> None:
    """Настройка обработчиков сообщений"""
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)) 