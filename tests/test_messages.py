"""
Тесты для шаблонов сообщений.
"""
import pytest
from src.ui.messages.message_manager import MessageManager

@pytest.fixture
def message_manager():
    """Фикстура для создания менеджера сообщений."""
    return MessageManager()

def test_welcome_message(message_manager):
    """Тест приветственного сообщения."""
    message = message_manager.get_welcome_message("test_user")
    
    assert isinstance(message, str)
    assert "test_user" in message
    assert "Добро пожаловать" in message
    assert "👋" in message

def test_help_message(message_manager):
    """Тест сообщения помощи."""
    message = message_manager.get_help_message()
    
    assert isinstance(message, str)
    assert "Доступные команды" in message
    assert "/start" in message
    assert "/help" in message

def test_error_message(message_manager):
    """Тест сообщения об ошибке."""
    message = message_manager.get_error_message()
    
    assert isinstance(message, str)
    assert "Произошла ошибка" in message

def test_topic_message(message_manager):
    """Тест сообщения о теме."""
    topic = {
        "title": "Test Topic",
        "description": "Test Description",
        "created_at": "2024-03-15"
    }
    message = message_manager.get_topic_message(topic)
    
    assert isinstance(message, str)
    assert topic["title"] in message
    assert topic["description"] in message

def test_vote_message(message_manager):
    """Тест сообщения о голосовании."""
    topics = [
        {'id': 1, 'topic': 'Test Topic', 'votes': 5},
        {'id': 2, 'topic': 'Another Topic', 'votes': 2}
    ]
    message = message_manager.get_vote_message(topics)
    
    assert isinstance(message, str)
    assert "Test Topic" in message
    assert "5" in message
    assert "2" in message

def test_success_message(message_manager):
    """Тест сообщения об успехе."""
    message = message_manager.get_learning_success_message("Test action")
    
    assert isinstance(message, str)
    assert "Test action" in message
    assert "✅" in message 