"""
Модуль для работы с метриками и мониторингом.
"""
from prometheus_client import Counter, Histogram, start_http_server
import structlog
import time
from functools import wraps
from typing import Callable, Any
from src.utils.mlflow_manager import MLflowManager

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
    
    def __init__(self):
        """Инициализация метрик."""
        self.mlflow_manager = MLflowManager()
    
    @classmethod
    def start_server(cls, port: int = 9090) -> None:
        """Запуск сервера метрик."""
        start_http_server(port)
        logger.info("metrics_server_started", port=port)
    
    def log_metrics(self, metrics: dict) -> None:
        """Логирование метрик в MLflow.
        
        Args:
            metrics: Словарь с метриками
        """
        try:
            self.mlflow_manager.log_metrics(metrics)
        except Exception as e:
            logger.error(f"Ошибка при логировании метрик в MLflow: {e}")
    
    def log_command_metrics(self, command: str, duration: float) -> None:
        """Логирование метрик команды.
        
        Args:
            command: Название команды
            duration: Длительность выполнения
        """
        try:
            # Обновляем Prometheus метрики
            self.command_counter.labels(command=command).inc()
            self.command_latency.observe(duration)
            
            # Логируем в MLflow
            self.mlflow_manager.start_run(run_name=f"command_{command}")
            self.mlflow_manager.log_metrics({
                f'command_{command}_count': 1,
                f'command_{command}_duration': duration
            })
            self.mlflow_manager.log_parameters({
                'command': command,
                'timestamp': time.time()
            })
            self.mlflow_manager.end_run()
        except Exception as e:
            logger.error(f"Ошибка при логировании метрик команды: {e}")
    
    def log_message_metrics(self, duration: float) -> None:
        """Логирование метрик сообщения.
        
        Args:
            duration: Длительность обработки
        """
        try:
            # Обновляем Prometheus метрики
            self.message_counter.inc()
            self.message_latency.observe(duration)
            
            # Логируем в MLflow
            self.mlflow_manager.start_run(run_name="message_processing")
            self.mlflow_manager.log_metrics({
                'message_count': 1,
                'message_duration': duration
            })
            self.mlflow_manager.log_parameters({
                'timestamp': time.time()
            })
            self.mlflow_manager.end_run()
        except Exception as e:
            logger.error(f"Ошибка при логировании метрик сообщения: {e}")
    
    def log_error_metrics(self, error_type: str) -> None:
        """Логирование метрик ошибки.
        
        Args:
            error_type: Тип ошибки
        """
        try:
            # Обновляем Prometheus метрики
            self.error_counter.labels(type=error_type).inc()
            
            # Логируем в MLflow
            self.mlflow_manager.start_run(run_name=f"error_{error_type}")
            self.mlflow_manager.log_metrics({
                f'error_{error_type}_count': 1
            })
            self.mlflow_manager.log_parameters({
                'error_type': error_type,
                'timestamp': time.time()
            })
            self.mlflow_manager.end_run()
        except Exception as e:
            logger.error(f"Ошибка при логировании метрик ошибки: {e}")
    
    def log_db_metrics(self, duration: float) -> None:
        """Логирование метрик базы данных.
        
        Args:
            duration: Длительность операции
        """
        try:
            # Обновляем Prometheus метрики
            self.db_latency.observe(duration)
            
            # Логируем в MLflow
            self.mlflow_manager.start_run(run_name="db_operation")
            self.mlflow_manager.log_metrics({
                'db_operation_duration': duration
            })
            self.mlflow_manager.log_parameters({
                'timestamp': time.time()
            })
            self.mlflow_manager.end_run()
        except Exception as e:
            logger.error(f"Ошибка при логировании метрик БД: {e}")
    
    def get_latest_metrics(self, metric_name: str, limit: int = 10) -> list:
        """Получение последних метрик.
        
        Args:
            metric_name: Название метрики
            limit: Количество последних значений
            
        Returns:
            Список последних значений метрики
        """
        try:
            return self.mlflow_manager.get_latest_metrics(metric_name, limit)
        except Exception as e:
            logger.error(f"Ошибка при получении последних метрик: {e}")
            return []

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