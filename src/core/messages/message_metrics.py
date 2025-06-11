"""
Модуль для отслеживания эффективности обработки сообщений.
"""
from typing import Dict, List, Optional
import logging
from datetime import datetime
from src.utils.database.db_manager import DatabaseManager
from src.utils.mlflow_manager import MLflowManager
from src.utils.metrics import Metrics

logger = logging.getLogger(__name__)

class MessageMetrics:
    """Класс для отслеживания эффективности обработки сообщений."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Инициализация отслеживания сообщений.
        
        Args:
            db_manager: Менеджер базы данных
        """
        self.db_manager = db_manager
        self.mlflow_manager = MLflowManager()
        self.metrics = Metrics()
        self._initialized = False

    async def initialize(self) -> None:
        """Инициализация отслеживания сообщений."""
        if not self._initialized:
            try:
                async with self.db_manager.get_connection() as conn:
                    await conn.execute(
                        """
                        CREATE TABLE IF NOT EXISTS message_metrics (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            message_type TEXT NOT NULL,
                            duration REAL NOT NULL,
                            success BOOLEAN NOT NULL,
                            error_message TEXT,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                    await conn.commit()
                self._initialized = True
                logger.info("MessageMetrics успешно инициализирован")
            except Exception as e:
                logger.error(f"Ошибка при инициализации MessageMetrics: {e}")
                raise

    async def track_message(self, user_id: int, message_type: str, duration: float, success: bool, error_message: Optional[str] = None) -> Dict:
        """
        Отслеживание обработки сообщения.
        
        Args:
            user_id: ID пользователя
            message_type: Тип сообщения
            duration: Длительность обработки
            success: Успешность обработки
            error_message: Сообщение об ошибке
            
        Returns:
            Dict: Результат отслеживания
        """
        try:
            # Начинаем новый запуск в MLflow
            self.mlflow_manager.start_run(run_name=f"message_{message_type}_{user_id}")

            # Логируем метрики
            self.mlflow_manager.log_metrics({
                "duration": duration,
                "success": 1.0 if success else 0.0
            })

            # Логируем параметры
            self.mlflow_manager.log_parameters({
                "message_type": message_type,
                "user_id": str(user_id),
                "timestamp": datetime.now().isoformat()
            })

            # Обновляем Prometheus метрики
            self.metrics.log_message_metrics(duration)
            if not success:
                self.metrics.log_error_metrics(f"message_{message_type}_error")

            # Сохраняем в базу данных
            async with self.db_manager.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO message_metrics (
                        user_id, message_type, duration, success, error_message
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, message_type, duration, success, error_message)
                )
                await conn.commit()

            # Завершаем запуск
            self.mlflow_manager.end_run()

            return {
                "status": "success",
                "message": "Метрики сообщения успешно сохранены"
            }
        except Exception as e:
            logger.error(f"Ошибка при отслеживании сообщения: {e}")
            return {
                "status": "error",
                "message": "Произошла ошибка при сохранении метрик"
            }

    async def get_message_stats(self, message_type: str) -> Dict:
        """
        Получение статистики по типу сообщений.
        
        Args:
            message_type: Тип сообщения
            
        Returns:
            Dict: Статистика сообщений
        """
        try:
            # Получаем из базы данных
            async with self.db_manager.get_connection() as conn:
                # Общее количество сообщений
                async with conn.execute(
                    "SELECT COUNT(*) as total FROM message_metrics WHERE message_type = ?",
                    (message_type,)
                ) as cursor:
                    total_messages = (await cursor.fetchone())['total']

                # Успешные сообщения
                async with conn.execute(
                    "SELECT COUNT(*) as success FROM message_metrics WHERE message_type = ? AND success = 1",
                    (message_type,)
                ) as cursor:
                    success_messages = (await cursor.fetchone())['success']

                # Средняя длительность
                async with conn.execute(
                    "SELECT AVG(duration) as avg_duration FROM message_metrics WHERE message_type = ?",
                    (message_type,)
                ) as cursor:
                    avg_duration = (await cursor.fetchone())['avg_duration'] or 0.0

                # Последние ошибки
                async with conn.execute(
                    """
                    SELECT error_message, timestamp
                    FROM message_metrics
                    WHERE message_type = ? AND success = 0
                    ORDER BY timestamp DESC
                    LIMIT 5
                    """,
                    (message_type,)
                ) as cursor:
                    recent_errors = await cursor.fetchall()

            # Получаем метрики из MLflow
            mlflow_metrics = self.mlflow_manager.get_latest_metrics(
                f"message_{message_type}_duration",
                limit=1
            )

            stats = {
                "total_messages": total_messages,
                "success_rate": (success_messages / total_messages * 100) if total_messages > 0 else 0.0,
                "average_duration": avg_duration,
                "recent_errors": [
                    {
                        "message": row['error_message'],
                        "timestamp": row['timestamp']
                    }
                    for row in recent_errors
                ]
            }

            # Обновляем метрики из MLflow
            if mlflow_metrics:
                stats['mlflow_metrics'] = mlflow_metrics[0].get('metrics', {})

            return {
                "status": "success",
                "stats": stats
            }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики сообщений: {e}")
            return {
                "status": "error",
                "message": "Произошла ошибка при получении статистики"
            }

    async def get_user_message_stats(self, user_id: int) -> Dict:
        """
        Получение статистики сообщений пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict: Статистика сообщений пользователя
        """
        try:
            # Получаем из базы данных
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(
                    """
                    SELECT message_type,
                           COUNT(*) as total_messages,
                           SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_messages,
                           AVG(duration) as avg_duration
                    FROM message_metrics
                    WHERE user_id = ?
                    GROUP BY message_type
                    """,
                    (user_id,)
                ) as cursor:
                    message_stats = await cursor.fetchall()

            # Получаем метрики из MLflow
            mlflow_metrics = self.mlflow_manager.get_latest_metrics(
                f"user_{user_id}_message_duration",
                limit=10
            )

            stats = {
                "messages": {},
                "total_messages": 0,
                "success_rate": 0.0,
                "average_duration": 0.0
            }

            # Обрабатываем статистику сообщений
            total_messages = 0
            total_success = 0
            total_duration = 0.0

            for row in message_stats:
                message_type = row['message_type']
                stats['messages'][message_type] = {
                    "total_messages": row['total_messages'],
                    "success_rate": (row['success_messages'] / row['total_messages'] * 100) if row['total_messages'] > 0 else 0.0,
                    "average_duration": row['avg_duration'] or 0.0
                }

                total_messages += row['total_messages']
                total_success += row['success_messages']
                total_duration += (row['avg_duration'] or 0.0) * row['total_messages']

            if total_messages > 0:
                stats['total_messages'] = total_messages
                stats['success_rate'] = (total_success / total_messages * 100)
                stats['average_duration'] = total_duration / total_messages

            # Обновляем метрики из MLflow
            if mlflow_metrics:
                stats['mlflow_metrics'] = [
                    run.get('metrics', {})
                    for run in mlflow_metrics
                ]

            return {
                "status": "success",
                "stats": stats
            }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики сообщений пользователя: {e}")
            return {
                "status": "error",
                "message": "Произошла ошибка при получении статистики"
            } 