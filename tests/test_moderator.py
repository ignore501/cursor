"""
Тесты для модуля модерации (vote_manager.py).
"""
import pytest
import pytest_asyncio
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
from src.core.moderation.vote_manager import VoteManager
from src.utils.database.db_manager import DatabaseManager
from telegram import Update, Message, User
from telegram.ext import ContextTypes
from typing import AsyncGenerator, Dict, Any
import tempfile
import os

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
        await db.close()
        os.unlink(db_path)

@pytest_asyncio.fixture
async def moderator(db_async: DatabaseManager) -> AsyncGenerator[VoteManager, None]:
    """Фикстура для создания менеджера голосований."""
    yield VoteManager(db_async)

@pytest.mark.asyncio
class TestVoteManager:
    """Тесты для класса VoteManager."""

    async def test_init(self, moderator: VoteManager) -> None:
        """Проверка инициализации менеджера голосований."""
        assert moderator is not None
        assert hasattr(moderator, "db_manager")

    @pytest.mark.asyncio
    async def test_create_vote(self, moderator: VoteManager, db_async: DatabaseManager) -> None:
        """Проверка создания голосования."""
        topic = "Test Topic"
        success = await moderator.create_vote(topic)
        assert success is True

        # Проверяем, что тема создана в базе
        topics = await db_async.get_topics()
        assert len(topics) == 1
        assert topics[0]["topic"] == topic

    @pytest.mark.asyncio
    async def test_add_vote(self, moderator: VoteManager, db_async: DatabaseManager) -> None:
        """Проверка добавления голоса."""
        # Создаем тему
        topic = "Test Topic"
        await moderator.create_vote(topic)
        topics = await db_async.get_topics()
        topic_id = topics[0]["id"]

        # Добавляем голос
        success = await moderator.add_vote(topic_id)
        assert success is True

        # Проверяем, что голос увеличился
        topic_row = (await db_async.get_topics())[0]
        assert topic_row["votes"] == 1

    @pytest.mark.asyncio
    async def test_get_top_topics(self, moderator: VoteManager, db_async: DatabaseManager) -> None:
        """Проверка получения топ тем."""
        # Создаем несколько тем
        topics = ["Topic 1", "Topic 2", "Topic 3"]
        for topic in topics:
            await moderator.create_vote(topic)

        # Получаем топ темы
        top_topics = await moderator.get_top_topics(limit=2)
        assert len(top_topics) == 2
        assert all(isinstance(topic, dict) for topic in top_topics)

    @pytest.mark.asyncio
    async def test_get_vote_results(self, moderator: VoteManager, db_async: DatabaseManager) -> None:
        """Проверка получения результатов голосования."""
        # Создаем тему
        topic = "Test Topic"
        await moderator.create_vote(topic)
        topics = await db_async.get_topics()
        topic_id = topics[0]["id"]

        # Добавляем голос
        await moderator.add_vote(topic_id)

        # Получаем результаты
        results = await moderator.get_vote_results(topic_id)
        assert results is not None
        assert results["topic"] == topic
        assert results["votes"] == 1

@pytest.mark.parametrize("topic,expected_success", [
    ("Valid Topic", True),
    ("", False),
    ("Topic with special chars !@#$%", True)
])
@pytest.mark.asyncio
async def test_create_vote_parametrized(
    moderator: VoteManager,
    db_async: DatabaseManager,
    topic: str,
    expected_success: bool
) -> None:
    """Параметризованный тест создания голосования."""
    success = await moderator.create_vote(topic)
    assert success == expected_success

    if expected_success:
        topics = await db_async.get_topics()
        assert len(topics) == 1
        assert topics[0]["topic"] == topic

@pytest.mark.parametrize("vote_count,expected_votes", [
    (1, 1),
    (5, 5),
    (10, 10)
])
@pytest.mark.asyncio
async def test_add_vote_parametrized(
    moderator: VoteManager,
    db_async: DatabaseManager,
    vote_count: int,
    expected_votes: int
) -> None:
    """Параметризованный тест добавления голосов."""
    # Создаем тему
    topic = "Test Topic"
    await moderator.create_vote(topic)
    topics = await db_async.get_topics()
    topic_id = topics[0]["id"]

    # Добавляем указанное количество голосов
    for _ in range(vote_count):
        await moderator.add_vote(topic_id)

    # Проверяем результаты
    results = await moderator.get_vote_results(topic_id)
    assert results is not None
    assert results["votes"] == expected_votes 