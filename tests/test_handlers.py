"""
Тесты для обработчиков команд.
"""
import pytest
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock
from telegram import Update, Message, User, Chat
from telegram.ext import CallbackContext
from src.bot.handlers.command_handlers import CommandHandlers
from src.utils.database.db_manager import DatabaseManager
import tempfile
import os
import aiosqlite
from collections.abc import AsyncGenerator
from src.core.moderation.vote_manager import VoteManager

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
async def update() -> AsyncGenerator[MagicMock, None]:
    """Фикстура для тестового обновления."""
    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(spec=User)
    update.effective_user.id = 123
    update.effective_user.username = "test_user"
    update.effective_user.first_name = "Test"
    update.effective_user.last_name = "User"
    update.effective_message = MagicMock(spec=Message)
    update.effective_message.chat = MagicMock(spec=Chat)
    update.effective_message.chat.id = 456
    yield update

@pytest_asyncio.fixture
async def context() -> AsyncGenerator[MagicMock, None]:
    """Фикстура для тестового контекста."""
    context = MagicMock(spec=CallbackContext)
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    yield context

@pytest_asyncio.fixture
async def command_handlers(db_async: DatabaseManager) -> CommandHandlers:
    """Фикстура для создания обработчиков команд."""
    return CommandHandlers(db_async, VoteManager(db_async)) 