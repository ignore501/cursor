"""
Тесты для основного модуля бота (autopost.py).
"""
import pytest
from unittest.mock import patch, MagicMock

from scripts.autopost import KaggleLearningBot

class TestKaggleLearningBot:
    """Тесты для класса KaggleLearningBot."""

    @pytest.fixture
    def bot(self, mock_env_vars):
        """Создает экземпляр бота для тестов."""
        with patch("telegram.ext.Application") as mock_app:
            bot = KaggleLearningBot()
            bot.app = mock_app
            yield bot

    def test_init(self, bot):
        """Проверка инициализации бота."""
        assert bot.app is not None
        assert bot.post_generator is not None
        assert bot.moderator is not None

    def test_start_command(self, bot, mock_update, mock_context):
        """Проверка команды /start."""
        with patch.object(bot.app, "send_message") as mock_send:
            bot.start(mock_update, mock_context)
            mock_send.assert_called_once()

    def test_help_command(self, bot, mock_update, mock_context):
        """Проверка команды /help."""
        with patch.object(bot.app, "send_message") as mock_send:
            bot.help_command(mock_update, mock_context)
            mock_send.assert_called_once()

    def test_vote_topic_command(self, bot, mock_update, mock_context):
        """Проверка команды /vote_topic."""
        mock_update.message.text = "/vote_topic Test Topic"
        with patch.object(bot.app, "send_message") as mock_send:
            bot.vote_topic(mock_update, mock_context)
            mock_send.assert_called_once()

    def test_vote_topic_no_args(self, bot, mock_update, mock_context):
        """Проверка команды /vote_topic без аргументов."""
        mock_update.message.text = "/vote_topic"
        with patch.object(bot.app, "send_message") as mock_send:
            bot.vote_topic(mock_update, mock_context)
            mock_send.assert_called_once()
            assert "Укажите тему" in mock_send.call_args[0][1]

    def test_morning_post(self, bot):
        """Проверка генерации утреннего поста."""
        with patch.object(bot.post_generator, "generate_morning_post") as mock_gen, \
             patch.object(bot.app, "send_message") as mock_send:
            mock_gen.return_value = "Test morning post"
            bot.morning_post()
            mock_send.assert_called_once()

    def test_evening_post(self, bot):
        """Проверка генерации вечернего поста."""
        with patch.object(bot.post_generator, "generate_evening_post") as mock_gen, \
             patch.object(bot.app, "send_message") as mock_send:
            mock_gen.return_value = "Test evening post"
            bot.evening_post()
            mock_send.assert_called_once()

    def test_get_today_metrics(self, bot, mock_mlflow):
        """Проверка получения метрик за день."""
        mock_mlflow.return_value = [{"metrics": {"accuracy": 0.95}}]
        metrics = bot.get_today_metrics()
        assert "accuracy" in metrics
        assert metrics["accuracy"] == 0.95

    def test_moderate_message(self, bot, mock_update):
        """Проверка модерации сообщений."""
        mock_update.message.text = "Test message"
        with patch.object(bot.moderator, "check_message") as mock_check:
            mock_check.return_value = (True, None)
            result = bot.moderate_message(mock_update)
            assert result is True

    def test_user_stats_command(self, bot, mock_update, mock_context):
        """Проверка команды /stats."""
        with patch.object(bot.moderator, "get_user_stats") as mock_stats, \
             patch.object(bot.app, "send_message") as mock_send:
            mock_stats.return_value = {"messages": 10, "warnings": 0}
            bot.user_stats(mock_update, mock_context)
            mock_send.assert_called_once()

    def test_unblock_command(self, bot, mock_update, mock_context):
        """Проверка команды /unblock."""
        mock_update.message.text = "/unblock 123456"
        with patch.object(bot.moderator, "unblock_user") as mock_unblock, \
             patch.object(bot.app, "send_message") as mock_send:
            mock_unblock.return_value = True
            bot.unblock_user(mock_update, mock_context)
            mock_send.assert_called_once() 