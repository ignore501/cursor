"""
Тесты для клавиатур.
"""
import pytest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from src.ui.keyboards.keyboard_manager import KeyboardManager

def test_get_main_menu():
    """Тест получения главного меню."""
    keyboard = KeyboardManager.get_main_menu()
    
    assert isinstance(keyboard, ReplyKeyboardMarkup)
    assert len(keyboard.keyboard) == 2
    assert len(keyboard.keyboard[0]) == 2
    assert len(keyboard.keyboard[1]) == 2
    
    # Проверяем точные значения кнопок
    assert [btn.text for btn in keyboard.keyboard[0]] == ["📊 Статистика", "📝 План"]
    assert [btn.text for btn in keyboard.keyboard[1]] == ["🗳 Голосование", "❓ Помощь"]

def test_get_vote_keyboard():
    """Тест получения клавиатуры для голосования."""
    topics = [
        {"id": 1, "topic": "Topic 1", "votes": 5},
        {"id": 2, "topic": "Topic 2", "votes": 3}
    ]
    keyboard = KeyboardManager.get_vote_keyboard(topics)
    
    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == len(topics)
    
    # Проверяем все кнопки одной строкой
    assert all(
        len(row) == 1 and 
        isinstance(row[0], InlineKeyboardButton) and
        row[0].text == f"{topic['topic']} ({topic['votes']})" and
        row[0].callback_data == f"vote_{topic['id']}"
        for row, topic in zip(keyboard.inline_keyboard, topics)
    )

def test_get_learning_menu():
    """Тест получения меню обучения."""
    keyboard = KeyboardManager.get_learning_menu()
    
    assert isinstance(keyboard, ReplyKeyboardMarkup)
    assert len(keyboard.keyboard) == 2
    assert len(keyboard.keyboard[0]) == 2
    assert len(keyboard.keyboard[1]) == 2
    
    # Проверяем точные значения кнопок
    assert [btn.text for btn in keyboard.keyboard[0]] == ["📚 Материалы", "📈 Прогресс"]
    assert [btn.text for btn in keyboard.keyboard[1]] == ["🏆 Достижения", "🔙 Назад"]

def test_get_confirmation_keyboard():
    """Тест получения клавиатуры подтверждения."""
    keyboard = KeyboardManager.get_confirmation_keyboard()
    
    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 1
    assert len(keyboard.inline_keyboard[0]) == 2
    
    buttons = keyboard.inline_keyboard[0]
    assert buttons[0].text == "✅ Да"
    assert buttons[0].callback_data == "confirm_yes"
    assert buttons[1].text == "❌ Нет"
    assert buttons[1].callback_data == "confirm_no" 