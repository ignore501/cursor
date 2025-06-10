"""
Модуль для работы с метриками и мониторингом.
"""
from prometheus_client import Counter, Histogram, start_http_server
import structlog
import time
from functools import wraps
from typing import Callable, Any

# Настройка структурированного логирования
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Метрики
class Metrics:
    # Счетчики
    message_counter = Counter('bot_messages_total', 'Total messages processed')
    command_counter = Counter('bot_commands_total', 'Total commands processed', ['command'])
    error_counter = Counter('bot_errors_total', 'Total errors', ['type'])
    
    # Гистограммы
    message_latency = Histogram('message_processing_seconds', 'Message processing time')
    command_latency = Histogram('command_processing_seconds', 'Command processing time')
    db_latency = Histogram('database_operation_seconds', 'Database operation time')
    
    @classmethod
    def start_server(cls, port: int = 9090) -> None:
        """Запуск сервера метрик."""
        start_http_server(port)
        logger.info("metrics_server_started", port=port)

def track_time(metric: Histogram) -> Callable:
    """Декоратор для отслеживания времени выполнения."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            with metric.time():
                return await func(*args, **kwargs)
        return wrapper
    return decorator

def log_error(error_type: str) -> Callable:
    """Декоратор для логирования ошибок."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                Metrics.error_counter.labels(type=error_type).inc()
                logger.error("operation_failed",
                           error_type=error_type,
                           error=str(e),
                           exc_info=True)
                raise
        return wrapper
    return decorator 