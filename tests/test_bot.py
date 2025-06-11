"""
Тесты для основного класса бота.
"""
import pytest
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock, Mock
from telegram import Update, Message, User, Chat
from telegram.ext import CallbackContext, Application
from src.bot.bot import Bot
from src.utils.database.db_manager import DatabaseManager
import tempfile
import os
from typing import AsyncGenerator

@pytest_asyncio.fixture
async def db_async() -> AsyncGenerator[DatabaseManager, None]:
    """Фикстура для тестовой базы данных."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        db_path = tmp.name
    db = DatabaseManager(db_path)
    await db.init_db()
    try:
        yield db
    finally:
        os.unlink(db_path)
        await db.close()

@pytest_asyncio.fixture
async def bot(db_async: DatabaseManager) -> AsyncGenerator[Bot, None]:
    """Фикстура для тестового бота."""
    yield Bot(db_async, "test_token")

@pytest.fixture
def mock_update() -> Mock:
    """Фикстура для мока Update."""
    update = Mock(spec=Update)
    update.message = Mock(spec=Message)
    update.message.chat = Mock(spec=Chat)
    update.message.chat.id = 123
    update.message.from_user = Mock(spec=User)
    update.message.from_user.id = 456
    update.message.from_user.username = "test_user"
    update.message.from_user.first_name = "Test"
    return update

@pytest.fixture
def mock_context() -> Mock:
    """Фикстура для мока Context."""
    context = Mock(spec=CallbackContext)
    context.bot = Mock()
    context.bot.send_message = AsyncMock()
    return context

@pytest.mark.asyncio
async def test_bot_initialization(bot: Bot) -> None:
    """Тест инициализации бота."""
    assert bot.db is not None
    assert bot.app is not None
    assert bot.command_handlers is not None

@pytest.mark.asyncio
async def test_start_command(bot: Bot, mock_update: Mock, mock_context: Mock) -> None:
    """Тест команды /start."""
    await bot.command_handlers.start(mock_update, mock_context)
    
    # Проверяем, что сообщение было отправлено
    mock_context.bot.send_message.assert_called_once()
    
    # Проверяем параметры сообщения
    call_args = mock_context.bot.send_message.call_args[1]
    assert call_args["chat_id"] == mock_update.message.chat.id
    assert "Добро пожаловать" in call_args["text"]
    assert "test_user" in call_args["text"]

@pytest.mark.asyncio
async def test_help_command(bot: Bot, mock_update: Mock, mock_context: Mock) -> None:
    """Тест команды /help."""
    await bot.command_handlers.help_command(mock_update, mock_context)
    
    # Проверяем, что сообщение было отправлено
    mock_context.bot.send_message.assert_called_once()
    
    # Проверяем параметры сообщения
    call_args = mock_context.bot.send_message.call_args[1]
    assert call_args["chat_id"] == mock_update.message.chat.id
    assert "Доступные команды" in call_args["text"]
    assert "/start" in call_args["text"]
    assert "/help" in call_args["text"]

@pytest.mark.asyncio
async def test_handle_error(bot: Bot, mock_update: Mock, mock_context: Mock) -> None:
    """Тест обработки ошибок."""
    mock_context.error = Exception("Test error")
    await bot.handle_error(mock_update, mock_context)
    
    # Проверяем, что сообщение об ошибке было отправлено
    mock_context.bot.send_message.assert_called_once()
    
    # Проверяем параметры сообщения
    call_args = mock_context.bot.send_message.call_args[1]
    assert call_args["chat_id"] == mock_update.message.chat.id
    assert "Произошла ошибка" in call_args["text"] 