"""
Модуль для управления клавиатурами.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class KeyboardManager:
    @staticmethod
    def get_main_menu() -> ReplyKeyboardMarkup:
        """Главное меню"""
        keyboard = [
            ["📊 Статистика", "📝 План"],
            ["🗳 Голосование", "🏆 Соревнования"],
            ["❓ Помощь"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def get_help_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура помощи"""
        keyboard = [
            [
                InlineKeyboardButton("📚 Документация", callback_data="help_docs"),
                InlineKeyboardButton("❓ FAQ", callback_data="help_faq")
            ],
            [
                InlineKeyboardButton("📞 Поддержка", callback_data="help_support"),
                InlineKeyboardButton("🔙 Назад", callback_data="help_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_stats_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура статистики"""
        keyboard = [
            [
                InlineKeyboardButton("📈 Прогресс", callback_data="stats_progress"),
                InlineKeyboardButton("🏆 Достижения", callback_data="stats_achievements")
            ],
            [
                InlineKeyboardButton("📊 Рейтинг", callback_data="stats_rating"),
                InlineKeyboardButton("🔙 Назад", callback_data="stats_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_plan_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура плана обучения"""
        keyboard = [
            [
                InlineKeyboardButton("📚 Материалы", callback_data="plan_materials"),
                InlineKeyboardButton("📝 Задания", callback_data="plan_tasks")
            ],
            [
                InlineKeyboardButton("📅 Расписание", callback_data="plan_schedule"),
                InlineKeyboardButton("🔙 Назад", callback_data="plan_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_vote_keyboard(topics: List[Dict]) -> InlineKeyboardMarkup:
        """Клавиатура для голосования"""
        keyboard = []
        keyboard.extend(
            [
                InlineKeyboardButton(
                    f"{topic['topic']} ({topic['votes']})",
                    callback_data=f"vote_{topic['id']}",
                )
            ]
            for topic in topics
        )
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_learning_menu() -> ReplyKeyboardMarkup:
        """Меню обучения"""
        keyboard = [
            ["📚 Материалы", "📈 Прогресс"],
            ["🏆 Достижения", "🔙 Назад"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def get_confirmation_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура подтверждения"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Да", callback_data="confirm_yes"),
                InlineKeyboardButton("❌ Нет", callback_data="confirm_no")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_competition_keyboard(competitions: List[Dict]) -> InlineKeyboardMarkup:
        """Клавиатура для выбора соревнования"""
        keyboard = []
        for comp in competitions:
            status = "✅" if comp['status'] == 'active' else "❌"
            keyboard.append([
                InlineKeyboardButton(
                    f"{status} {comp['title']}",
                    callback_data=f"comp_{comp['competition_id']}"
                )
            ])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_competition_keyboard() -> InlineKeyboardMarkup:
        """Создает клавиатуру для управления соревнованиями"""
        keyboard = [
            [
                InlineKeyboardButton("Список соревнований", callback_data="competition_list"),
                InlineKeyboardButton("Создать соревнование", callback_data="competition_create")
            ],
            [
                InlineKeyboardButton("Мои соревнования", callback_data="competition_my"),
                InlineKeyboardButton("Статистика", callback_data="competition_stats")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_topic_keyboard(topic_id: int) -> InlineKeyboardMarkup:
        """Создает клавиатуру для голосования за тему"""
        keyboard = [
            [
                InlineKeyboardButton("👍", callback_data=f"vote_up_{topic_id}"),
                InlineKeyboardButton("👎", callback_data=f"vote_down_{topic_id}")
            ],
            [
                InlineKeyboardButton("Комментарии", callback_data=f"topic_comments_{topic_id}"),
                InlineKeyboardButton("Закрыть", callback_data="close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_learning_keyboard() -> InlineKeyboardMarkup:
        """Создает клавиатуру для управления обучением"""
        keyboard = [
            [
                InlineKeyboardButton("Начать обучение", callback_data="learn_start"),
                InlineKeyboardButton("Мой прогресс", callback_data="learn_progress")
            ],
            [
                InlineKeyboardButton("Материалы", callback_data="learn_materials"),
                InlineKeyboardButton("Тесты", callback_data="learn_tests")
            ]
        ]
        return InlineKeyboardMarkup(keyboard) 