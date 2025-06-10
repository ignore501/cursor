"""
Тесты для модуля генерации постов (post_templates.py).
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from scripts.post_templates import PostGenerator

class TestPostGenerator:
    """Тесты для класса PostGenerator."""

    @pytest.fixture
    def generator(self, temp_dir, sample_plan):
        """Создает экземпляр генератора постов для тестов."""
        return PostGenerator(temp_dir)

    def test_init(self, generator, temp_dir):
        """Проверка инициализации генератора."""
        assert generator.data_dir == temp_dir
        assert generator.learning_plan is not None

    def test_load_learning_plan(self, generator, sample_plan):
        """Проверка загрузки плана обучения."""
        plan = generator._load_learning_plan()
        assert "topics" in plan
        assert len(plan["topics"]) > 0

    def test_get_today_tasks(self, generator):
        """Проверка получения задач на сегодня."""
        with patch("datetime.datetime") as mock_date:
            mock_date.now.return_value = datetime(2024, 1, 1)
            tasks = generator.get_today_tasks()
            assert isinstance(tasks, list)
            assert len(tasks) > 0

    def test_generate_morning_post(self, generator):
        """Проверка генерации утреннего поста."""
        with patch("datetime.datetime") as mock_date:
            mock_date.now.return_value = datetime(2024, 1, 1)
            post = generator.generate_morning_post()
            assert isinstance(post, str)
            assert "План на" in post
            assert "Задачи" in post

    def test_generate_evening_post(self, generator):
        """Проверка генерации вечернего поста."""
        with patch("datetime.datetime") as mock_date:
            mock_date.now.return_value = datetime(2024, 1, 1)
            metrics = {"accuracy": 0.95, "loss": 0.05}
            post = generator.generate_evening_post(metrics)
            assert isinstance(post, str)
            assert "Итоги дня" in post
            assert "Метрики" in post

    def test_generate_evening_post_no_metrics(self, generator):
        """Проверка генерации вечернего поста без метрик."""
        with patch("datetime.datetime") as mock_date:
            mock_date.now.return_value = datetime(2024, 1, 1)
            post = generator.generate_evening_post({})
            assert isinstance(post, str)
            assert "Итоги дня" in post
            assert "Метрики не найдены" in post

    def test_summarize_results(self, generator):
        """Проверка суммаризации результатов."""
        text = "Это тестовый текст для суммаризации. " * 10
        with patch("transformers.pipeline") as mock_pipeline:
            mock_pipeline.return_value = MagicMock(return_value=[{"summary_text": "Краткое содержание"}])
            summary = generator._summarize_results(text)
            assert isinstance(summary, str)
            assert len(summary) < len(text)

    def test_get_next_topic(self, generator):
        """Проверка получения следующей темы."""
        with patch("datetime.datetime") as mock_date:
            mock_date.now.return_value = datetime(2024, 1, 1)
            topic = generator.get_next_topic()
            assert isinstance(topic, str)
            assert len(topic) > 0 