"""
Общие фикстуры для тестов.
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from telegram import Update
from telegram.ext import CallbackContext

# Фикстура для временной директории
@pytest.fixture
def temp_dir():
    """Создает временную директорию для тестов."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

# Фикстура для мока Telegram Update
@pytest.fixture
def mock_update():
    """Создает мок объекта Update для тестирования команд."""
    update = MagicMock(spec=Update)
    update.effective_user.id = 123456
    update.effective_user.username = "test_user"
    update.message.text = "/test"
    return update

# Фикстура для мока CallbackContext
@pytest.fixture
def mock_context():
    """Создает мок объекта CallbackContext для тестирования команд."""
    context = MagicMock(spec=CallbackContext)
    return context

# Фикстура для мока MLflow
@pytest.fixture
def mock_mlflow():
    """Создает мок MLflow для тестирования метрик."""
    with patch("mlflow.get_experiment_by_name") as mock_get_exp, \
         patch("mlflow.search_runs") as mock_search:
        mock_get_exp.return_value = MagicMock(experiment_id=1)
        mock_search.return_value = []
        yield mock_search

# Фикстура для тестового Jupyter ноутбука
@pytest.fixture
def sample_notebook(temp_dir):
    """Создает тестовый Jupyter ноутбук."""
    notebook_path = temp_dir / "test_notebook.ipynb"
    notebook_content = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "accuracy = 0.95\n",
                    "loss = 0.05\n",
                    "f1_score = 0.94"
                ],
                "outputs": []
            },
            {
                "cell_type": "markdown",
                "source": [
                    "# Тестовый заголовок\n",
                    "Описание эксперимента"
                ]
            }
        ]
    }
    import json
    with open(notebook_path, "w") as f:
        json.dump(notebook_content, f)
    return notebook_path

# Фикстура для тестового плана обучения
@pytest.fixture
def sample_plan(temp_dir):
    """Создает тестовый план обучения."""
    plan_path = temp_dir / "plan.json"
    plan_content = {
        "topics": [
            {
                "name": "Test Topic",
                "tasks": ["Task 1", "Task 2"],
                "schedule": "2024-01-01"
            }
        ]
    }
    import json
    with open(plan_path, "w") as f:
        json.dump(plan_content, f)
    return plan_path

# Фикстура для тестовых переменных окружения
@pytest.fixture
def mock_env_vars():
    """Устанавливает тестовые переменные окружения."""
    env_vars = {
        "TELEGRAM_BOT_TOKEN": "test_token",
        "CHANNEL_ID": "-100123456789",
        "MLFLOW_TRACKING_URI": "http://localhost:5000"
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars 