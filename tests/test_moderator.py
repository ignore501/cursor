"""
Тесты для модуля модерации (moderator.py).
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.moderation.moderator import Moderator
from src.database.database import Database

class TestModerator:
    """Тесты для класса Moderator."""

    @pytest.fixture
    def db(self):
        return Database(":memory:")

    @pytest.fixture
    def moderator(self, db):
        return Moderator(db)

    def test_init(self, moderator):
        """Проверка инициализации модератора."""
        assert moderator.banned_words is not None
        assert moderator.spam_patterns is not None
        assert moderator.user_stats is not None
        assert moderator.blocked_users is not None

    def test_check_message_valid(self, moderator):
        """Проверка валидного сообщения."""
        message = "Привет, как дела?"
        is_valid, reason = moderator.check_message(message, 123456)
        assert is_valid is True
        assert reason is None

    def test_check_message_banned_words(self, moderator):
        """Проверка сообщения с запрещенными словами."""
        message = "Спам реклама купить"
        is_valid, reason = moderator.check_message(message, 123456)
        assert is_valid is False
        assert "запрещенные слова" in reason.lower()

    def test_check_message_spam(self, moderator):
        """Проверка спам-сообщения."""
        message = "!!!!! СПАМ !!!!!"
        is_valid, reason = moderator.check_message(message, 123456)
        assert is_valid is False
        assert "спам" in reason.lower()

    def test_check_message_rate_limit(self, moderator):
        """Проверка ограничения частоты сообщений."""
        user_id = 123456
        # Отправляем сообщения быстрее лимита
        for _ in range(6):
            is_valid, _ = moderator.check_message("test", user_id)
        is_valid, reason = moderator.check_message("test", user_id)
        assert is_valid is False
        assert "слишком часто" in reason.lower()

    def test_handle_violation(self, moderator):
        """Проверка обработки нарушения."""
        user_id = 123456
        # Первое нарушение
        moderator.handle_violation(user_id)
        assert user_id not in moderator.blocked_users
        assert moderator.user_stats[user_id]["warnings"] == 1

        # Второе нарушение
        moderator.handle_violation(user_id)
        assert user_id not in moderator.blocked_users
        assert moderator.user_stats[user_id]["warnings"] == 2

        # Третье нарушение (блокировка)
        moderator.handle_violation(user_id)
        assert user_id in moderator.blocked_users
        assert moderator.user_stats[user_id]["warnings"] == 3

    def test_unblock_user(self, moderator):
        """Проверка разблокировки пользователя."""
        user_id = 123456
        moderator.blocked_users.add(user_id)
        moderator.user_stats[user_id] = {"warnings": 3, "messages": 10}
        
        success = moderator.unblock_user(user_id)
        assert success is True
        assert user_id not in moderator.blocked_users
        assert moderator.user_stats[user_id]["warnings"] == 0

    def test_get_user_stats(self, moderator, db):
        """Проверка получения статистики пользователя."""
        user_id = 1
        chat_id = 1

        # Добавляем тестовые сообщения
        for _ in range(5):
            db.add_message(user_id, chat_id, "test message")

        # Тест на получение статистики
        stats = moderator.get_user_stats(user_id)
        assert stats["total_messages"] == 5
        assert stats["warnings"] == 0
        assert stats["is_banned"] is False

    def test_reset_user_stats(self, moderator):
        """Проверка сброса статистики пользователя."""
        user_id = 123456
        moderator.user_stats[user_id] = {
            "messages": 10,
            "warnings": 2,
            "last_message": datetime.now()
        }
        
        moderator.reset_user_stats(user_id)
        assert user_id not in moderator.user_stats

    def test_check_message_blocked_user(self, moderator):
        """Проверка сообщения от заблокированного пользователя."""
        user_id = 123456
        moderator.blocked_users.add(user_id)
        
        is_valid, reason = moderator.check_message("test", user_id)
        assert is_valid is False
        assert "заблокирован" in reason.lower()

    def test_check_message_frequency(self, moderator, db):
        # Тест на нормальную частоту сообщений
        user_id = 1
        assert moderator._check_message_frequency(user_id) is True

        # Тест на слишком частые сообщения
        for _ in range(6):
            db.add_message(user_id, 1, "test message")
        assert moderator._check_message_frequency(user_id) is False

    def test_check_message_length(self, moderator):
        # Тест на нормальную длину сообщения
        assert moderator._check_message_length("Normal message") is True

        # Тест на слишком длинное сообщение
        long_message = "a" * 1001
        assert moderator._check_message_length(long_message) is False

    def test_check_spam(self, moderator, db):
        assert "заблокирован" in reason.lower() 