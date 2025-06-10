"""
Модуль для генерации постов с использованием шаблонов Jinja2.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import jinja2
from transformers import pipeline

from config import (
    BART_MODEL_NAME,
    JUPYTER_TEMPLATES_DIR,
    MAX_LENGTH,
    MIN_LENGTH,
)
from scripts.database import Database

class PostGenerator:
    """Класс для генерации постов с использованием шаблонов."""

    def __init__(self, data_dir: Path):
        """Инициализация генератора постов."""
        # Загрузка шаблонов
        self.template_loader = jinja2.FileSystemLoader(searchpath=str(JUPYTER_TEMPLATES_DIR))
        self.template_env = jinja2.Environment(loader=self.template_loader)
        
        # Загрузка плана обучения
        self.learning_plan = self._load_learning_plan(data_dir)
        
        # Инициализация модели для суммаризации
        self.summarizer = pipeline(
            "summarization",
            model=BART_MODEL_NAME,
            max_length=MAX_LENGTH,
            min_length=MIN_LENGTH,
        )
        
        # Инициализация базы данных
        self.db = Database()

    def _load_learning_plan(self, data_dir: Path) -> dict:
        """Загрузка плана обучения из JSON файла."""
        plan_file = data_dir / "plan.json"
        if not plan_file.exists():
            return {"topics": [], "schedule": {}}
        
        with open(plan_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_morning_post(self) -> str:
        """Генерация утреннего поста."""
        template = self.template_env.get_template("morning_post.md")
        
        # Получение темы дня
        today = datetime.now().strftime("%Y-%m-%d")
        topic = self.learning_plan["schedule"].get(today, "Обзор и практика")
        
        # Получение популярных тем для голосования
        voting_topics = self.db.get_voting_topics(limit=5)
        
        # Генерация поста
        post = template.render(
            date=today,
            topic=topic,
            tasks=self._get_today_tasks(topic),
            voting_topics=voting_topics
        )
        
        return post

    def generate_evening_post(self, metrics: Dict) -> str:
        """Генерация вечернего поста."""
        template = self.template_env.get_template("evening_post.md")
        
        # Суммаризация результатов
        summary = self._summarize_results(metrics)
        
        # Получение статистики активности
        activity_stats = self._get_activity_stats()
        
        # Генерация поста
        post = template.render(
            date=datetime.now().strftime("%Y-%m-%d"),
            summary=summary,
            metrics=metrics,
            next_topic=self._get_next_topic(),
            activity_stats=activity_stats
        )
        
        return post

    def _get_today_tasks(self, topic: str) -> List[str]:
        """Получение списка задач на день."""
        tasks = []
        for t in self.learning_plan["topics"]:
            if t["name"] == topic:
                tasks = t.get("tasks", [])
                break
        return tasks

    def _summarize_results(self, metrics: Dict) -> str:
        """Суммаризация результатов дня."""
        # TODO: Реализовать сбор текста из Jupyter ноутбуков
        text = "Сегодня мы работали над улучшением модели..."
        
        # Добавление метрик в текст
        text += f"\n\nДостигнутые результаты:\n"
        for metric_name, value in metrics.items():
            text += f"- {metric_name}: {value:.4f}\n"
        
        # Суммаризация с помощью BART
        summary = self.summarizer(text, max_length=MAX_LENGTH, min_length=MIN_LENGTH)[0]["summary_text"]
        return summary

    def _get_next_topic(self) -> str:
        """Получение следующей темы для изучения."""
        today = datetime.now().strftime("%Y-%m-%d")
        schedule = self.learning_plan["schedule"]
        
        # Поиск следующей темы в расписании
        next_topics = [date for date in schedule.keys() if date > today]
        if next_topics:
            return schedule[next_topics[0]]
            
        # Если нет запланированных тем, используем популярные темы из голосования
        voting_topics = self.db.get_voting_topics(limit=1)
        if voting_topics:
            return voting_topics[0][1]  # topic_id, topic, votes, created_at
            
        return "Повторение и закрепление материала"

    def _get_activity_stats(self) -> Dict:
        """Получение статистики активности за день."""
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Получение количества сообщений за последние два дня
        today_messages = self.db.get_message_count(None, timedelta(days=1))
        yesterday_messages = self.db.get_message_count(None, timedelta(days=2)) - today_messages
        
        return {
            "today_messages": today_messages,
            "yesterday_messages": yesterday_messages,
            "change_percent": ((today_messages - yesterday_messages) / yesterday_messages * 100) if yesterday_messages > 0 else 0
        } 