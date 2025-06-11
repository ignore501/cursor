"""
Тесты для работы с базой данных.
"""
import pytest
import pytest_asyncio
pytest_plugins = ["pytest_asyncio"]
from src.utils.database.db_manager import DatabaseManager
import os
from typing import AsyncGenerator
import aiosqlite
from datetime import datetime

@pytest_asyncio.fixture
async def db() -> DatabaseManager:
    """Фикстура для создания тестовой базы данных."""
    test_db_path = "test_database.db"
    db = DatabaseManager(test_db_path)
    await db.initialize()
    try:
        yield db
    finally:
        await db.close()  # Сначала закрываем соединение
        if os.path.exists(test_db_path):
            try:
                os.remove(test_db_path)
            except PermissionError:
                pass  # Игнорируем ошибку, если файл все еще занят

@pytest.mark.asyncio
async def test_database_initialization(db):
    """Тест инициализации базы данных."""
    assert db is not None
    assert db.connection is not None

@pytest.mark.asyncio
async def test_user_operations(db):
    """Тест операций с пользователями."""
    user_id = 123
    username = "test_user"
    first_name = "Test"
    last_name = "User"
    
    # Добавление пользователя
    await db.add_user(user_id, username, first_name, last_name)
    
    # Получение пользователя
    user = await db.get_user(user_id)
    assert user is not None
    assert user["user_id"] == user_id
    assert user["username"] == username
    assert user["first_name"] == first_name
    assert user["last_name"] == last_name
    
    # Проверка блокировки
    assert await db.is_user_blocked(user_id) is False
    await db.block_user(user_id)
    assert await db.is_user_blocked(user_id) is True
    await db.unblock_user(user_id)
    assert await db.is_user_blocked(user_id) is False

@pytest.mark.asyncio
async def test_message_operations(db):
    """Тест операций с сообщениями."""
    user_id = 123
    message_text = "Test message"
    
    # Очищаем предыдущие сообщения
    async with aiosqlite.connect(db.db_path) as conn:
        await conn.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
        await conn.commit()
    
    # Добавление сообщения
    message_id = await db.add_message(user_id, message_text)
    assert message_id is not None
    
    # Получение сообщения
    message = await db.get_message(message_id)
    assert message is not None
    assert message["user_id"] == user_id
    assert message["text"] == message_text
    
    # Получение сообщений пользователя
    messages = await db.get_user_messages(user_id)
    assert len(messages) == 1
    assert messages[0]["text"] == message_text

@pytest.mark.asyncio
async def test_topic_operations(db):
    """Тест операций с темами."""
    user_id = 123
    topic = "Test topic"
    
    # Очищаем предыдущие темы
    async with aiosqlite.connect(db.db_path) as conn:
        await conn.execute("DELETE FROM topics")
        await conn.commit()
    
    # Добавление темы
    topic_id = await db.add_topic(topic)
    assert topic_id is not None
    
    # Получение темы
    topic_data = await db.get_topic(topic_id)
    assert topic_data is not None
    assert topic_data["id"] == topic_id
    assert topic_data["topic"] == topic

@pytest.mark.asyncio
async def test_vote_operations(db):
    """Тест операций с голосами."""
    user_id = 123
    topic = "Test topic"
    
    # Добавление темы
    topic_id = await db.add_topic(topic)
    
    # Добавление голоса
    vote_type = "up"
    await db.add_vote(user_id, topic_id, vote_type)
    
    # Получение голосов
    votes = await db.get_votes(topic_id)
    assert len(votes) == 1
    assert votes[0]["user_id"] == user_id
    assert votes[0]["topic_id"] == topic_id
    assert votes[0]["vote_type"] == vote_type

@pytest.mark.asyncio
async def test_user_stats(db):
    """Тест получения статистики пользователя."""
    user_id = 123
    username = "test_user"
    
    # Очищаем предыдущие данные
    async with aiosqlite.connect(db.db_path) as conn:
        await conn.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
        await conn.execute("DELETE FROM topics")
        await conn.commit()
    
    # Добавление пользователя
    await db.add_user(user_id, username)
    
    # Добавление сообщений и тем
    await db.add_message(user_id, "Message 1")
    await db.add_message(user_id, "Message 2")
    await db.add_topic("Test topic")
    
    # Получение статистики
    stats = await db.get_user_stats(user_id)
    assert stats is not None
    assert stats["message_count"] == 2
    assert stats["topic_count"] == 1 