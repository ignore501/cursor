"""
Тесты для обработчиков команд бота.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, Message, Chat, User, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from src.bot.handlers.command_handlers import CommandHandlers
from src.utils.database.db_manager import DatabaseManager
from src.core.moderation.vote_manager import VoteManager
from src.ui.messages.message_manager import MessageManager
from src.ui.keyboards.keyboard_manager import KeyboardManager

@pytest.fixture
def mock_db_manager():
    """Фикстура для мока DatabaseManager."""
    return AsyncMock(spec=DatabaseManager)

@pytest.fixture
def mock_vote_manager():
    """Фикстура для мока VoteManager."""
    return AsyncMock(spec=VoteManager)

@pytest.fixture
def command_handlers(mock_db_manager, mock_vote_manager):
    """Фикстура для CommandHandlers с моками."""
    return CommandHandlers(mock_db_manager, mock_vote_manager)

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

@pytest.fixture
def command_handlers() -> CommandHandlers:
    """Фикстура для обработчиков команд."""
    db_manager = Mock(spec=DatabaseManager)
    vote_manager = Mock(spec=VoteManager)
    
    # Настраиваем моки для возврата тестовых данных
    vote_manager.get_top_topics = AsyncMock(return_value=[
        {'id': 1, 'topic': 'Test Topic 1', 'votes': 5},
        {'id': 2, 'topic': 'Test Topic 2', 'votes': 3}
    ])
    
    # Создаем экземпляр CommandHandlers
    handlers = CommandHandlers(db_manager, vote_manager)
    
    # Мокаем методы message_manager и keyboard_manager
    handlers.message_manager.get_welcome_message.return_value = "Добро пожаловать!"
    handlers.message_manager.get_help_message.return_value = "Справка"
    handlers.message_manager.get_stats_message.return_value = "Статистика"
    handlers.message_manager.get_vote_message.return_value = "Тема: Test Topic 1\nID: 1\nВсего голосов: 5\n\nТема: Test Topic 2\nID: 2\nВсего голосов: 3\n"
    handlers.message_manager.get_plan_message.return_value = "План обучения"
    
    # Создаем тестовые клавиатуры
    main_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
    ])
    learning_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обучение", callback_data="learning")]
    ])
    vote_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Test Topic 1 (5)", callback_data="vote_1")],
        [InlineKeyboardButton(text="Test Topic 2 (3)", callback_data="vote_2")]
    ])
    
    handlers.keyboard_manager.get_main_menu.return_value = main_menu
    handlers.keyboard_manager.get_learning_menu.return_value = learning_menu
    handlers.keyboard_manager.get_vote_keyboard.return_value = vote_keyboard
    
    return handlers

@pytest.mark.asyncio
async def test_start_command(command_handlers: CommandHandlers, mock_update: Mock, mock_context: Mock) -> None:
    """Тест команды /start."""
    await command_handlers.start(mock_update, mock_context)
    
    mock_context.bot.send_message.assert_called_once_with(
        chat_id=mock_update.message.chat.id,
        text=command_handlers.message_manager.get_welcome_message(mock_update.message.from_user.username),
        reply_markup=command_handlers.keyboard_manager.get_main_menu()
    )

@pytest.mark.asyncio
async def test_help_command(command_handlers: CommandHandlers, mock_update: Mock, mock_context: Mock) -> None:
    """Тест команды /help."""
    await command_handlers.help_command(mock_update, mock_context)
    
    mock_context.bot.send_message.assert_called_once_with(
        chat_id=mock_update.message.chat.id,
        text=command_handlers.message_manager.get_help_message(),
        reply_markup=command_handlers.keyboard_manager.get_main_menu()
    )

@pytest.mark.asyncio
async def test_stats_command(command_handlers: CommandHandlers, mock_update: Mock, mock_context: Mock) -> None:
    """Тест команды /stats."""
    await command_handlers.stats(mock_update, mock_context)
    
    mock_context.bot.send_message.assert_called_once_with(
        chat_id=mock_update.message.chat.id,
        text=command_handlers.message_manager.get_stats_message({
            'completed_tasks': 0,
            'progress': 0,
            'learning_time': '0ч',
            'achievements': 0
        }),
        reply_markup=command_handlers.keyboard_manager.get_learning_menu()
    )

@pytest.mark.asyncio
async def test_vote_command(command_handlers: CommandHandlers, mock_update: Mock, mock_context: Mock) -> None:
    """Тест команды /vote."""
    await command_handlers.vote(mock_update, mock_context)
    
    mock_context.bot.send_message.assert_called_once_with(
        chat_id=mock_update.message.chat.id,
        text=command_handlers.message_manager.get_vote_message([
            {'id': 1, 'topic': 'Test Topic 1', 'votes': 5},
            {'id': 2, 'topic': 'Test Topic 2', 'votes': 3}
        ]),
        reply_markup=command_handlers.keyboard_manager.get_vote_keyboard([
            {'id': 1, 'topic': 'Test Topic 1', 'votes': 5},
            {'id': 2, 'topic': 'Test Topic 2', 'votes': 3}
        ])
    )

@pytest.mark.asyncio
async def test_plan_command(command_handlers: CommandHandlers, mock_update: Mock, mock_context: Mock) -> None:
    """Тест команды /plan."""
    await command_handlers.plan(mock_update, mock_context)
    
    mock_context.bot.send_message.assert_called_once_with(
        chat_id=mock_update.message.chat.id,
        text=command_handlers.message_manager.get_plan_message({
            'goal': 'Изучение машинного обучения',
            'materials': 'Курс на Kaggle',
            'time': '2 часа'
        }),
        reply_markup=command_handlers.keyboard_manager.get_learning_menu()
    ) 