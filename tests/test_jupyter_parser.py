"""
Тесты для модуля парсинга Jupyter ноутбуков (notebook_parser.py).
"""
import pytest
from typing import Dict
from src.core.learning.notebook_parser import NotebookParser

@pytest.fixture
def notebook_parser() -> NotebookParser:
    """Фикстура для создания парсера ноутбуков."""
    return NotebookParser()

@pytest.fixture
def sample_notebook() -> Dict:
    """Фикстура с примером ноутбука."""
    return {
        "cells": [
            {
                "cell_type": "code",
                "source": ["accuracy = 0.95\n", "loss = 0.1"],
                "outputs": [],
            },
            {"cell_type": "markdown", "source": ["# Test Notebook"]},
        ]
    }

def test_parse_notebook(notebook_parser: NotebookParser, sample_notebook: Dict):
    """Тест парсинга ноутбука."""
    result = notebook_parser.parse_notebook(sample_notebook)
    assert isinstance(result, dict)
    assert "metrics" in result
    assert "code_snippets" in result
    assert "plots" in result
    assert "summary" in result

def test_parse_notebook_with_invalid_cell(notebook_parser: NotebookParser):
    """Тест парсинга ноутбука с невалидной ячейкой."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": ["invalid code"],
                "outputs": []
            }
        ]
    }
    result = notebook_parser.parse_notebook(notebook)
    assert isinstance(result, dict)
    assert "metrics" in result
    assert "code_snippets" in result

def test_parse_notebook_with_empty_cells(notebook_parser: NotebookParser):
    """Тест парсинга ноутбука с пустыми ячейками."""
    notebook = {"cells": []}
    result = notebook_parser.parse_notebook(notebook)
    assert isinstance(result, dict)
    assert result["metrics"] == {}
    assert result["code_snippets"] == []
    assert result["plots"] == []
    assert result["summary"] == ""

def test_parse_notebook_with_missing_metadata(notebook_parser: NotebookParser):
    """Тест парсинга ноутбука с отсутствующими метаданными."""
    notebook = {}
    result = notebook_parser.parse_notebook(notebook)
    assert isinstance(result, dict)
    assert result["metrics"] == {}
    assert result["code_snippets"] == []
    assert result["plots"] == []
    assert result["summary"] == ""

def test_get_notebook_metrics(notebook_parser: NotebookParser, sample_notebook: Dict):
    """Тест получения метрик из ноутбука."""
    metrics = notebook_parser.get_notebook_metrics(sample_notebook)
    assert isinstance(metrics, dict)
    assert metrics.get("accuracy") == 0.95
    assert metrics.get("loss") == 0.1 