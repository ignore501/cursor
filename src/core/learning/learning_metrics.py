"""
Модуль для работы с метриками обучения.
"""
from typing import Dict, List, Optional
import logging
from datetime import datetime
from src.utils.database.db_manager import DatabaseManager
from src.utils.mlflow_manager import MLflowManager

logger = logging.getLogger(__name__)

class LearningMetrics:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.mlflow_manager = MLflowManager()
        self._initialized = False

    async def initialize(self) -> None:
        """Инициализация метрик обучения"""
        if not self._initialized:
            try:
                async with self.db_manager.get_connection() as conn:
                    # Проверяем наличие необходимых таблиц
                    await self.db_manager.check_tables(conn)
                self._initialized = True
                logger.info("LearningMetrics успешно инициализирован")
            except Exception as e:
                logger.error(f"Ошибка при инициализации LearningMetrics: {e}")
                raise

    async def log_metric(self, user_id: int, metric_name: str, value: float) -> Dict:
        """Логирование метрики обучения"""
        try:
            # Сохраняем в базу данных
            async with self.db_manager.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO learning_metrics (user_id, metric_name, value, timestamp)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, metric_name, value, datetime.now())
                )
                await conn.commit()

            # Логируем в MLflow
            self.mlflow_manager.log_metrics({
                f"user_{user_id}_{metric_name}": value
            })

            return {
                "status": "success",
                "message": "Метрика успешно сохранена"
            }
        except Exception as e:
            logger.error(f"Ошибка при логировании метрики: {e}")
            return {
                "status": "error",
                "message": "Произошла ошибка при сохранении метрики"
            }

    async def get_user_metrics(self, user_id: int) -> Dict:
        """Получение метрик пользователя"""
        try:
            # Получаем из базы данных
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(
                    """
                    SELECT metric_name, value, timestamp
                    FROM learning_metrics
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    """,
                    (user_id,)
                ) as cursor:
                    rows = await cursor.fetchall()

            # Получаем последние метрики из MLflow
            mlflow_metrics = self.mlflow_manager.get_latest_metrics(
                f"user_{user_id}_accuracy",
                limit=1
            )

            metrics = {
                "accuracy": 0.0,
                "completion_rate": 0.0,
                "time_spent": 0
            }

            # Обновляем метрики из базы данных
            for row in rows:
                if row['metric_name'] in metrics:
                    metrics[row['metric_name']] = row['value']

            # Обновляем метрики из MLflow
            if mlflow_metrics:
                metrics['accuracy'] = mlflow_metrics[0].get('metrics', {}).get('accuracy', 0.0)

            return {
                "status": "success",
                "metrics": metrics
            }
        except Exception as e:
            logger.error(f"Ошибка при получении метрик пользователя: {e}")
            return {
                "status": "error",
                "message": "Произошла ошибка при получении метрик"
            }

    async def get_global_metrics(self) -> Dict:
        """Получение глобальных метрик обучения"""
        try:
            # Получаем из базы данных
            async with self.db_manager.get_connection() as conn:
                # Общее количество пользователей
                async with conn.execute(
                    "SELECT COUNT(DISTINCT user_id) as total FROM learning_metrics"
                ) as cursor:
                    total_users = (await cursor.fetchone())['total']

                # Активные пользователи (за последние 24 часа)
                async with conn.execute(
                    """
                    SELECT COUNT(DISTINCT user_id) as active
                    FROM learning_metrics
                    WHERE timestamp >= datetime('now', '-1 day')
                    """
                ) as cursor:
                    active_users = (await cursor.fetchone())['active']

                # Средние метрики
                async with conn.execute(
                    """
                    SELECT AVG(value) as avg_accuracy
                    FROM learning_metrics
                    WHERE metric_name = 'accuracy'
                    """
                ) as cursor:
                    avg_accuracy = (await cursor.fetchone())['avg_accuracy'] or 0.0

                async with conn.execute(
                    """
                    SELECT AVG(value) as avg_completion
                    FROM learning_metrics
                    WHERE metric_name = 'completion_rate'
                    """
                ) as cursor:
                    avg_completion = (await cursor.fetchone())['avg_completion'] or 0.0

            if mlflow_metrics := self.mlflow_manager.get_latest_metrics(
                "global_accuracy", limit=1
            ):
                avg_accuracy = mlflow_metrics[0].get('metrics', {}).get('accuracy', avg_accuracy)

            return {
                "status": "success",
                "metrics": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "average_accuracy": avg_accuracy,
                    "average_completion_rate": avg_completion
                }
            }
        except Exception as e:
            logger.error(f"Ошибка при получении глобальных метрик: {e}")
            return {
                "status": "error",
                "message": "Произошла ошибка при получении глобальных метрик"
            }

    async def log_learning_session(self, user_id: int, duration: int, accuracy: float) -> Dict:
        """Логирование сессии обучения"""
        try:
            # Начинаем новый запуск в MLflow
            self.mlflow_manager.start_run(run_name=f"learning_session_{user_id}")

            # Логируем метрики
            self.mlflow_manager.log_metrics({
                "duration": duration,
                "accuracy": accuracy
            })

            # Логируем параметры
            self.mlflow_manager.log_parameters({
                "user_id": str(user_id),
                "session_type": "learning"
            })

            # Сохраняем в базу данных
            await self.log_metric(user_id, "time_spent", duration)
            await self.log_metric(user_id, "accuracy", accuracy)

            # Завершаем запуск
            self.mlflow_manager.end_run()

            return {
                "status": "success",
                "message": "Сессия обучения успешно залогирована"
            }
        except Exception as e:
            logger.error(f"Ошибка при логировании сессии обучения: {e}")
            return {
                "status": "error",
                "message": "Произошла ошибка при логировании сессии"
            }

    async def update_user_progress(self, user_id: int, progress_data: Dict) -> Dict:
        """Обновление прогресса пользователя"""
        try:
            async with self.db_manager.get_connection() as conn:
                # TODO: Реализовать обновление прогресса в базе данных
                return {
                    "status": "success",
                    "message": "Прогресс успешно обновлен"
                }
        except Exception as e:
            logger.error(f"Ошибка при обновлении прогресса пользователя: {e}")
            return {
                "status": "error",
                "message": "Произошла ошибка при обновлении прогресса"
            } 