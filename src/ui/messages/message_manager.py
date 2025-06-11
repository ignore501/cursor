"""
Менеджер сообщений.
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class MessageManager:
    """Менеджер сообщений."""

    def __init__(self):
        """Инициализация менеджера сообщений."""
        self.templates = {
            'welcome': "Привет, {username}! Я бот для изучения программирования. Чем могу помочь?",
            'help': "Доступные команды:\n/start - Начать работу\n/help - Показать помощь\n/stats - Статистика\n/vote - Голосование\n/plan - План обучения",
            'error': "Произошла ошибка. Пожалуйста, попробуйте позже.",
            'vote': "Темы для голосования:\n{topics}",
            'vote_topic': "{title}\nГолосов: {votes}\nВаш голос: {user_vote}",
            'no_topics': "Нет доступных тем для голосования.",
            'stats': "Ваша статистика:\nВыполнено заданий: {completed_tasks}\nПрогресс: {progress}%\nВремя обучения: {learning_time}\nДостижения: {achievements}",
            'plan': "Ваш план обучения:\nЦель: {goal}\nМатериалы: {materials}\nВремя: {time}"
        }

    def get_welcome_message(self, username: str) -> str:
        """Получение приветственного сообщения."""
        return self.templates['welcome'].format(username=username)

    def get_help_message(self) -> str:
        """Получение сообщения с помощью."""
        return self.templates['help']

    def get_error_message(self) -> str:
        """Получение сообщения об ошибке."""
        return self.templates['error']

    def get_vote_message(self, topics: List[Dict[str, Any]]) -> str:
        """Получение сообщения для голосования."""
        if not topics:
            return self.templates['no_topics']
        
        topics_text = []
        for topic in topics:
            topic_text = self.templates['vote_topic'].format(
                title=topic.get('title', 'Без названия'),
                votes=topic.get('votes', 0),
                user_vote=topic.get('user_vote', 'Нет')
            )
            topics_text.append(topic_text)
        
        return self.templates['vote'].format(topics='\n\n'.join(topics_text))

    def get_stats_message(self, stats: Dict[str, Any]) -> str:
        """Получение сообщения со статистикой."""
        return self.templates['stats'].format(
            completed_tasks=stats.get('completed_tasks', 0),
            progress=stats.get('progress', 0),
            learning_time=stats.get('learning_time', '0ч'),
            achievements=stats.get('achievements', 0)
        )

    def get_plan_message(self, plan: Dict[str, Any]) -> str:
        """Получение сообщения с планом обучения."""
        return self.templates['plan'].format(
            goal=plan.get('goal', 'Не указана'),
            materials=plan.get('materials', 'Не указаны'),
            time=plan.get('time', 'Не указано')
        ) 