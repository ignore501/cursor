"""
Общие фикстуры для тестов.
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock, Mock
from typing import AsyncGenerator, Generator, Dict, Any

import pytest
import pytest_asyncio
from telegram import Update, Message, User, Chat
from telegram.ext import CallbackContext
from src.utils.database.db_manager import DatabaseManager
from src.utils.logger import setup_logger
from src.config.config import Config
import aiosqlite
from src.bot.bot import Bot
from src.core.moderation.vote_manager import VoteManager

pytest_plugins = ["pytest_asyncio"]

# Инициализация логгера для тестов
logger = setup_logger("tests")

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Фикстура для временной директории."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest_asyncio.fixture
async def mock_update() -> AsyncGenerator[Update, None]:
    """Создает мок объекта Update для тестирования команд."""
    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(spec=User)
    update.effective_user.id = 123456
    update.effective_user.username = "test_user"
    update.effective_message = MagicMock(spec=Message)
    update.effective_message.text = "/test"
    yield update

@pytest_asyncio.fixture
async def mock_context() -> AsyncGenerator[CallbackContext, None]:
    """Создает мок объекта CallbackContext для тестирования команд."""
    context = MagicMock(spec=CallbackContext)
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    yield context

@pytest.fixture
def mock_mlflow() -> Generator[MagicMock, None, None]:
    """Создает мок MLflow для тестирования метрик."""
    with patch("mlflow.get_experiment_by_name") as mock_get_exp, \
         patch("mlflow.search_runs") as mock_search:
        mock_get_exp.return_value = MagicMock(experiment_id=1)
        mock_search.return_value = []
        yield mock_search

@pytest.fixture
def sample_notebook(temp_dir: Path) -> Generator[Path, None, None]:
    """Создает тестовый Jupyter ноутбук."""
    notebook_path = temp_dir / "test_notebook.ipynb"
    notebook_content = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "accuracy = 0.95\n",
                    "loss = 0.05\n",
                    "f1_score = 0.94"
                ],
                "outputs": []
            },
            {
                "cell_type": "markdown",
                "source": [
                    "# Тестовый заголовок\n",
                    "Описание эксперимента"
                ]
            }
        ]
    }
    import json
    with open(notebook_path, "w") as f:
        json.dump(notebook_content, f)
    yield notebook_path

@pytest.fixture
def mock_env_vars() -> Generator[Dict[str, str], None, None]:
    """Устанавливает тестовые переменные окружения."""
    env_vars = {
        "TELEGRAM_BOT_TOKEN": "test_token",
        "TELEGRAM_CHANNEL_ID": "-100123456789",
        "MLFLOW_TRACKING_URI": "http://localhost:5000"
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars

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

@pytest.fixture
def config() -> Generator[Config, None, None]:
    """Фикстура конфигурации."""
    yield Config()

@pytest_asyncio.fixture
async def temp_db() -> AsyncGenerator[DatabaseManager, None]:
    """Фикстура временной базы данных."""
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db = DatabaseManager(db_path)
    await db.init_db()
    try:
        yield db
    finally:
        await db.close()
        os.remove(db_path)

@pytest.fixture
def test_db_path():
    """Фикстура для тестовой базы данных."""
    db_path = Path("test.db")
    yield db_path
    if db_path.exists():
        db_path.unlink()

@pytest.fixture
def db_manager(test_db_path):
    """Фикстура для менеджера базы данных."""
    manager = DatabaseManager(str(test_db_path))
    yield manager
    manager.close()

@pytest.fixture(autouse=True)
def setup_test_env():
    """Фикстура для настройки тестового окружения."""
    # Сохраняем оригинальные значения
    original_env = dict(os.environ)
    
    # Устанавливаем тестовые значения
    os.environ.update({
        "TELEGRAM_TOKEN": "test_token",
        "TELEGRAM_ADMIN_IDS": "[123, 456]",
        "TELEGRAM_CHANNEL_ID": "test_channel",
        "KAGGLE_USERNAME": "test_user",
        "KAGGLE_KEY": "test_key",
        "COMPETITION_ID": "test_competition",
        "TELEGRAM_BOT_TOKEN": "test_bot_token"
    })
    
    yield
    
    # Восстанавливаем оригинальные значения
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def test_config() -> Dict[str, Any]:
    """
    Фикстура для тестовой конфигурации.
    
    Returns:
        Dict[str, Any]: Словарь с тестовой конфигурацией
    """
    return {
        "TELEGRAM_BOT_TOKEN": "test_token",
        "CHANNEL_ID": -100123456789,
        "ADMIN_IDS": [123456789],
        "EXPERIMENT_NAME": "test_experiment",
        "KAGGLE_DATASET_PATH": "test/dataset",
        "MLFLOW_TRACKING_URI": "http://localhost:5000"
    }

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

@pytest.fixture
def update():
    """Фикстура обновления Telegram."""
    return Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=None,
            chat=Chat(id=1, type='private'),
            from_user=User(id=1, is_bot=False, first_name='Test')
        )
    )

@pytest.fixture
def context():
    """Фикстура контекста Telegram."""
    return CallbackContext(None)

@pytest_asyncio.fixture
async def vote_manager(db_async: DatabaseManager) -> AsyncGenerator[VoteManager, None]:
    """Фикстура для менеджера голосования."""
    yield VoteManager(db_async)

@pytest_asyncio.fixture
async def bot(db_async: DatabaseManager, vote_manager: VoteManager) -> AsyncGenerator[Bot, None]:
    """Фикстура для тестового бота."""
    yield Bot(db_async)

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

# Тесты для фикстур
@pytest.mark.asyncio
async def test_db_async_fixture(db_async: DatabaseManager) -> None:
    """Тест фикстуры базы данных."""
    assert isinstance(db_async, DatabaseManager)
    assert db_async.db_path is not None
    await db_async.init_db()
    assert await db_async.get_user(1) is None

@pytest.mark.asyncio
async def test_vote_manager_fixture(vote_manager: VoteManager, db_async: DatabaseManager) -> None:
    """Тест фикстуры менеджера голосования."""
    assert isinstance(vote_manager, VoteManager)
    assert vote_manager.db_manager == db_async

@pytest.mark.asyncio
async def test_bot_fixture(bot: Bot, db_async: DatabaseManager) -> None:
    """Тест фикстуры бота."""
    assert isinstance(bot, Bot)
    assert bot.db == db_async

def test_mock_update_fixture(mock_update: Mock) -> None:
    """Тест фикстуры мока Update."""
    assert isinstance(mock_update, Mock)
    assert isinstance(mock_update.message, Mock)
    assert isinstance(mock_update.message.chat, Mock)
    assert isinstance(mock_update.message.from_user, Mock)
    assert mock_update.message.chat.id == 123
    assert mock_update.message.from_user.id == 456

@pytest.mark.asyncio
async def test_mock_context_fixture(mock_context: Mock) -> None:
    """Тест фикстуры мока Context."""
    assert isinstance(mock_context, Mock)
    assert isinstance(mock_context.bot, Mock)
    assert isinstance(mock_context.bot.send_message, AsyncMock)
    await mock_context.bot.send_message()
    mock_context.bot.send_message.assert_called_once()

def test_temp_dir_fixture(temp_dir: Path) -> None:
    """Тест фикстуры временной директории."""
    assert isinstance(temp_dir, Path)
    assert temp_dir.exists()
    assert temp_dir.is_dir() 