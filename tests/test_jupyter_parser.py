"""
Тесты для модуля парсинга Jupyter ноутбуков (jupyter_parser.py).
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from scripts.jupyter_parser import JupyterParser

class TestJupyterParser:
    """Тесты для класса JupyterParser."""

    @pytest.fixture
    def parser(self, temp_dir):
        """Создает экземпляр парсера для тестов."""
        return JupyterParser(temp_dir)

    def test_init(self, parser, temp_dir):
        """Проверка инициализации парсера."""
        assert parser.notebooks_dir == temp_dir
        assert parser.exporter is not None

    def test_parse_notebook(self, parser, sample_notebook):
        """Проверка парсинга ноутбука."""
        result = parser.parse_notebook(sample_notebook)
        assert isinstance(result, dict)
        assert "metrics" in result
        assert "code" in result
        assert "summary" in result

    def test_extract_metrics(self, parser):
        """Проверка извлечения метрик."""
        code = """
        accuracy = 0.95
        loss = 0.05
        f1_score = 0.94
        """
        metrics = parser._extract_metrics(code)
        assert "accuracy" in metrics
        assert "loss" in metrics
        assert "f1_score" in metrics
        assert metrics["accuracy"] == 0.95

    def test_extract_code(self, parser):
        """Проверка извлечения кода."""
        code = """
        # TODO: Fix this
        def test():
            pass
        # FIXME: Add error handling
        """
        code_snippets = parser._extract_code(code)
        assert len(code_snippets) == 0  # Код с TODO/FIXME игнорируется

        code = """
        def test():
            return True
        """
        code_snippets = parser._extract_code(code)
        assert len(code_snippets) > 0

    def test_extract_plots(self, parser):
        """Проверка извлечения графиков."""
        output = {
            "data": {
                "image/png": "base64_encoded_image"
            }
        }
        plots = parser._extract_plots(output)
        assert isinstance(plots, list)
        assert len(plots) > 0

    def test_generate_summary(self, parser):
        """Проверка генерации описания."""
        markdown = """
        # Заголовок 1
        Описание 1
        ## Подзаголовок
        Описание 2
        """
        summary = parser._generate_summary(markdown)
        assert isinstance(summary, str)
        assert "Заголовок 1" in summary
        assert "Описание 1" in summary

    def test_get_latest_notebook(self, parser, sample_notebook):
        """Проверка получения последнего ноутбука."""
        latest = parser.get_latest_notebook()
        assert isinstance(latest, Path)
        assert latest.exists()

    def test_get_notebook_metrics(self, parser, sample_notebook):
        """Проверка получения метрик ноутбука."""
        metrics_df = parser.get_notebook_metrics()
        assert not metrics_df.empty
        assert "accuracy" in metrics_df.columns
        assert "loss" in metrics_df.columns 