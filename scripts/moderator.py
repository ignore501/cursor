"""
Модуль для модерации комментариев и защиты от атак.
"""
import re
from typing import List, Optional
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from scripts.database import Database

class Moderator:
    """Класс для модерации комментариев и защиты от атак."""

    def __init__(self):
        """Инициализация модератора."""
        # Список запрещенных слов
        self.banned_words = [
            "спам", "реклама", "купить", "продать",
            "криптовалюта", "биткоин", "заработок",
            "казино", "ставки", "лотерея"
        ]
        
        # Регулярные выражения для проверки спама
        self.spam_patterns = [
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            r"\b\d{10,}\b"  # Длинные последовательности цифр
        ]
        
        # Ограничения на частоту сообщений
        self.message_limits = {
            "per_minute": 5,
            "per_hour": 20,
            "per_day": 100
        }
        
        # Инициализация базы данных
        self.db = Database()

    async def check_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Проверка сообщения на соответствие правилам.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            bool: True если сообщение прошло проверку, False если нет
        """
        if not update.message or not update.message.text:
            return True
            
        user = update.message.from_user
        user_id = user.id
        
        # Добавление пользователя в базу данных
        self.db.add_user(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Получение статистики пользователя
        stats = self.db.get_user_stats(user_id)
        
        # Проверка на блокировку
        if stats and stats["is_blocked"]:
            await update.message.reply_text(
                "Вы заблокированы за нарушение правил канала."
            )
            return False
            
        # Проверка частоты сообщений
        if not self._check_message_frequency(user_id):
            await update.message.reply_text(
                "Слишком много сообщений. Пожалуйста, подождите."
            )
            return False
            
        # Проверка на спам
        if self._is_spam(update.message.text):
            await self._handle_spam(update, context)
            return False
            
        # Проверка на запрещенные слова
        if self._contains_banned_words(update.message.text):
            await update.message.reply_text(
                "Ваше сообщение содержит запрещенные слова."
            )
            return False
            
        # Сохранение сообщения в базу данных
        self.db.add_message(user_id, update.message.text)
        return True

    def _check_message_frequency(self, user_id: int) -> bool:
        """Проверка частоты сообщений пользователя."""
        # Получение количества сообщений за разные периоды
        message_counts = self.db.get_messages_per_period(user_id)
        
        return (
            message_counts["per_minute"] <= self.message_limits["per_minute"] and
            message_counts["per_hour"] <= self.message_limits["per_hour"] and
            message_counts["per_day"] <= self.message_limits["per_day"]
        )

    def _is_spam(self, text: str) -> bool:
        """Проверка текста на спам."""
        # Проверка по регулярным выражениям
        for pattern in self.spam_patterns:
            if re.search(pattern, text):
                return True
                
        # Проверка на повторяющиеся символы
        if re.search(r"(.)\1{4,}", text):
            return True
            
        return False

    def _contains_banned_words(self, text: str) -> bool:
        """Проверка на наличие запрещенных слов."""
        text_lower = text.lower()
        return any(word in text_lower for word in self.banned_words)

    async def _handle_spam(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработка спам-сообщений."""
        user_id = update.message.from_user.id
        
        # Добавление предупреждения
        warnings = self.db.add_warning(user_id)
        
        if warnings >= 3:
            self.db.block_user(user_id)
            await update.message.reply_text(
                "Вы заблокированы за спам."
            )
        else:
            await update.message.reply_text(
                f"Предупреждение {warnings}/3: "
                "Обнаружен спам. Пожалуйста, соблюдайте правила канала."
            )

    def get_user_stats(self, user_id: int) -> Optional[dict]:
        """Получение статистики пользователя."""
        return self.db.get_user_stats(user_id)

    def unblock_user(self, user_id: int) -> None:
        """Разблокировка пользователя."""
        self.db.unblock_user(user_id) 