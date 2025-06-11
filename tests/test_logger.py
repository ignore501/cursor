"""
Тесты для модуля логирования.
"""
import pytest
import logging
from src.utils.logger import logger

def test_logger_instance():
    """Тест проверки экземпляра логгера."""
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.INFO
    assert logger.name == "src.utils.logger"

def test_logger_info_output(caplog):
    """Тест вывода INFO сообщения."""
    with caplog.at_level(logging.INFO):
        logger.info("Test info message")
        assert "Test info message" in caplog.text

def test_logger_error_output(caplog):
    """Тест вывода ERROR сообщения."""
    with caplog.at_level(logging.ERROR):
        logger.error("Test error message")
        assert "Test error message" in caplog.text

def test_logger_warning_output(caplog):
    """Тест вывода WARNING сообщения."""
    with caplog.at_level(logging.WARNING):
        logger.warning("Test warning message")
        assert "Test warning message" in caplog.text 