import pytest
from unittest.mock import MagicMock, patch
from telegram import Update, Message, Chat, User
from telegram.ext import CallbackContext
from src.bot.bot import Bot
from src.database.database import Database

@pytest.fixture
def db():
    return Database(":memory:")

@pytest.fixture
def bot(db):
    return Bot(db)

@pytest.fixture
def update():
    update = MagicMock(spec=Update)
    update.message = MagicMock(spec=Message)
    update.message.chat = MagicMock(spec=Chat)
    update.message.from_user = MagicMock(spec=User)
    return update

@pytest.fixture
def context():
    context = MagicMock(spec=CallbackContext)
    return context

def test_start_command(bot, update, context):
    # Тест команды /start
    update.message.text = "/start"
    update.message.from_user.id = 1
    update.message.from_user.username = "test_user"
    update.message.from_user.first_name = "Test"
    update.message.from_user.last_name = "User"

    bot.start_command(update, context)
    update.message.reply_text.assert_called_once()
    assert "Добро пожаловать" in update.message.reply_text.call_args[0][0]

def test_help_command(bot, update, context):
    # Тест команды /help
    update.message.text = "/help"
    bot.help_command(update, context)
    update.message.reply_text.assert_called_once()
    assert "Доступные команды" in update.message.reply_text.call_args[0][0]

def test_plan_command(bot, update, context):
    # Тест команды /plan
    update.message.text = "/plan"
    bot.plan_command(update, context)
    update.message.reply_text.assert_called_once()
    assert "План обучения" in update.message.reply_text.call_args[0][0]

def test_progress_command(bot, update, context):
    # Тест команды /progress
    update.message.text = "/progress"
    update.message.from_user.id = 1
    bot.progress_command(update, context)
    update.message.reply_text.assert_called_once()
    assert "Ваш прогресс" in update.message.reply_text.call_args[0][0]

def test_vote_topic_command(bot, update, context):
    # Тест команды /vote_topic
    update.message.text = "/vote_topic Feature Engineering"
    update.message.from_user.id = 1
    bot.vote_topic_command(update, context)
    update.message.reply_text.assert_called_once()
    assert "Ваш голос" in update.message.reply_text.call_args[0][0]

def test_ask_command(bot, update, context):
    # Тест команды /ask
    update.message.text = "/ask Как начать изучение Data Science?"
    update.message.from_user.id = 1
    bot.ask_command(update, context)
    update.message.reply_text.assert_called_once()
    assert "ответ" in update.message.reply_text.call_args[0][0].lower()

def test_feedback_command(bot, update, context):
    # Тест команды /feedback
    update.message.text = "/feedback 5 Отличный бот!"
    update.message.from_user.id = 1
    bot.feedback_command(update, context)
    update.message.reply_text.assert_called_once()
    assert "спасибо" in update.message.reply_text.call_args[0][0].lower()

def test_handle_message(bot, update, context):
    # Тест обработки обычного сообщения
    update.message.text = "Привет, бот!"
    update.message.from_user.id = 1
    bot.handle_message(update, context)
    update.message.reply_text.assert_called_once()
    assert "привет" in update.message.reply_text.call_args[0][0].lower()

def test_handle_error(bot, update, context):
    # Тест обработки ошибок
    error = Exception("Test error")
    bot.handle_error(update, context, error)
    assert context.bot.send_message.called

def test_check_user_status(bot, update):
    # Тест проверки статуса пользователя
    update.message.from_user.id = 1
    assert bot.check_user_status(update) is True

    # Тест для забаненного пользователя
    bot.db.ban_user(1, "Test ban", 3600)
    assert bot.check_user_status(update) is False

def test_send_morning_post(bot, context):
    # Тест отправки утреннего поста
    bot.send_morning_post(context)
    assert context.bot.send_message.called

def test_send_evening_post(bot, context):
    # Тест отправки вечернего поста
    bot.send_evening_post(context)
    assert context.bot.send_message.called

def test_send_reminder(bot, context):
    # Тест отправки напоминания
    bot.send_reminder(context)
    assert context.bot.send_message.called

def test_send_feedback_reminder(bot, context):
    # Тест отправки напоминания об отзыве
    bot.send_feedback_reminder(context)
    assert context.bot.send_message.called 