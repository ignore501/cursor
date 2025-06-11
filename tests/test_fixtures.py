"""
Тесты для фикстур.
"""
import pytest
import pytest_asyncio
from pathlib import Path
from unittest.mock import Mock
from telegram import Update, Message, User, Chat
from telegram.ext import CallbackContext

from src.utils.database.db_manager import DatabaseManager
from src.bot.bot import Bot
from src.core.moderation.vote_manager import VoteManager

@pytest.mark.asyncio
async def test_db_async_fixture(db_async: DatabaseManager) -> None:
    """Тест фикстуры базы данных."""
    assert isinstance(db_async, DatabaseManager)
    assert db_async.db_path is not None
    # Проверяем, что можем выполнить простой запрос
    await db_async.init_db()
    assert await db_async.get_user(1) is None

@pytest.mark.asyncio
async def test_vote_manager_fixture(vote_manager: VoteManager, db_async: DatabaseManager) -> None:
    """Тест фикстуры менеджера голосования."""
    assert isinstance(vote_manager, VoteManager)
    assert vote_manager.db_manager == db_async
    # Проверяем базовые методы
    topics = await vote_manager.get_top_topics()
    assert isinstance(topics, list)

@pytest.mark.asyncio
async def test_bot_fixture(bot: Bot, db_async: DatabaseManager) -> None:
    """Тест фикстуры бота."""
    assert isinstance(bot, Bot)
    assert bot.db == db_async
    assert bot.app is not None
    assert bot.command_handlers is not None

def test_mock_update_fixture(mock_update: Mock) -> None:
    """Тест фикстуры мока Update."""
    assert isinstance(mock_update, Mock)
    assert isinstance(mock_update.message, Mock)
    assert isinstance(mock_update.message.chat, Mock)
    assert isinstance(mock_update.message.from_user, Mock)
    assert mock_update.message.chat.id == 123
    assert mock_update.message.from_user.id == 456
    assert mock_update.message.from_user.username == "test_user"
    assert mock_update.message.from_user.first_name == "Test"

@pytest.mark.asyncio
async def test_mock_context_fixture(mock_context: Mock) -> None:
    """Тест фикстуры мока Context."""
    assert isinstance(mock_context, Mock)
    assert isinstance(mock_context.bot, Mock)
    assert isinstance(mock_context.bot.send_message, Mock)
    # Проверяем, что можем вызвать send_message
    mock_context.bot.send_message.return_value = None
    result = await mock_context.bot.send_message()
    assert result is None

def test_temp_dir(temp_dir: Path):
    """Тест фикстуры temp_dir."""
    assert isinstance(temp_dir, Path)
    assert temp_dir.exists()
    assert temp_dir.is_dir()

def test_sample_notebook(sample_notebook: Path):
    """Тест фикстуры sample_notebook."""
    assert isinstance(sample_notebook, Path)
    assert sample_notebook.exists()
    assert sample_notebook.suffix == '.ipynb'

def test_mock_env_vars(mock_env_vars: dict):
    """Тест фикстуры mock_env_vars."""
    assert isinstance(mock_env_vars, dict)
    assert "TELEGRAM_BOT_TOKEN" in mock_env_vars
    assert "TELEGRAM_CHANNEL_ID" in mock_env_vars
    assert "MLFLOW_TRACKING_URI" in mock_env_vars

@pytest.mark.asyncio
async def test_temp_db(temp_db: DatabaseManager):
    """Тест фикстуры temp_db."""
    assert isinstance(temp_db, DatabaseManager) 