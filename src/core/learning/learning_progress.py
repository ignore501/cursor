"""
Модуль для отслеживания прогресса обучения.
"""
from typing import Dict, List, Optional
import logging
from datetime import datetime
from src.utils.database.db_manager import DatabaseManager
from src.utils.mlflow_manager import MLflowManager
from src.core.learning.learning_metrics import LearningMetrics

logger = logging.getLogger(__name__)

class LearningProgress:
    """Класс для отслеживания прогресса обучения."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Инициализация отслеживания прогресса.
        
        Args:
            db_manager: Менеджер базы данных
        """
        self.db_manager = db_manager
        self.mlflow_manager = MLflowManager()
        self.learning_metrics = LearningMetrics(db_manager)
        self._initialized = False

    async def initialize(self) -> None:
        """Инициализация отслеживания прогресса."""
        if not self._initialized:
            try:
                await self.learning_metrics.initialize()
                self._initialized = True
                logger.info("LearningProgress успешно инициализирован")
            except Exception as e:
                logger.error(f"Ошибка при инициализации LearningProgress: {e}")
                raise

    async def track_progress(self, user_id: int, progress_data: Dict) -> Dict:
        """
        Отслеживание прогресса обучения.
        
        Args:
            user_id: ID пользователя
            progress_data: Данные о прогрессе
            
        Returns:
            Dict: Результат отслеживания
        """
        try:
            # Начинаем новый запуск в MLflow
            self.mlflow_manager.start_run(run_name=f"learning_progress_{user_id}")

            # Логируем метрики
            self.mlflow_manager.log_metrics({
                "completion_rate": progress_data.get("completion_rate", 0.0),
                "accuracy": progress_data.get("accuracy", 0.0),
                "time_spent": progress_data.get("time_spent", 0)
            })

            # Логируем параметры
            self.mlflow_manager.log_parameters({
                "user_id": str(user_id),
                "course": progress_data.get("course", "unknown"),
                "module": progress_data.get("module", "unknown"),
                "timestamp": datetime.now().isoformat()
            })

            # Сохраняем в базу данных
            async with self.db_manager.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO learning_progress (
                        user_id, course, module, completion_rate,
                        accuracy, time_spent, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        progress_data.get("course", "unknown"),
                        progress_data.get("module", "unknown"),
                        progress_data.get("completion_rate", 0.0),
                        progress_data.get("accuracy", 0.0),
                        progress_data.get("time_spent", 0),
                        datetime.now()
                    )
                )
                await conn.commit()

            # Завершаем запуск
            self.mlflow_manager.end_run()

            return {
                "status": "success",
                "message": "Прогресс успешно сохранен"
            }
        except Exception as e:
            logger.error(f"Ошибка при отслеживании прогресса: {e}")
            return {
                "status": "error",
                "message": "Произошла ошибка при сохранении прогресса"
            }

    async def get_user_progress(self, user_id: int) -> Dict:
        """
        Получение прогресса пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict: Прогресс пользователя
        """
        try:
            # Получаем из базы данных
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(
                    """
                    SELECT course, module, completion_rate, accuracy, time_spent, timestamp
                    FROM learning_progress
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    """,
                    (user_id,)
                ) as cursor:
                    rows = await cursor.fetchall()

            # Получаем последние метрики из MLflow
            mlflow_metrics = self.mlflow_manager.get_latest_metrics(
                f"user_{user_id}_completion_rate",
                limit=1
            )

            progress = {
                "courses": {},
                "total_time": 0,
                "average_accuracy": 0.0,
                "average_completion": 0.0
            }

            # Обрабатываем данные из базы
            for row in rows:
                course = row['course']
                if course not in progress['courses']:
                    progress['courses'][course] = {
                        "modules": {},
                        "total_time": 0,
                        "average_accuracy": 0.0,
                        "average_completion": 0.0
                    }

                module = row['module']
                progress['courses'][course]['modules'][module] = {
                    "completion_rate": row['completion_rate'],
                    "accuracy": row['accuracy'],
                    "time_spent": row['time_spent'],
                    "last_updated": row['timestamp']
                }

                progress['courses'][course]['total_time'] += row['time_spent']
                progress['total_time'] += row['time_spent']

            # Обновляем метрики из MLflow
            if mlflow_metrics:
                for course in progress['courses']:
                    if course_metrics := self.mlflow_manager.get_latest_metrics(
                        f"user_{user_id}_course_{course}_completion_rate", limit=1
                    ):
                        progress['courses'][course]['average_completion'] = course_metrics[0].get(
                            'metrics', {}
                        ).get('completion_rate', 0.0)

            return {
                "status": "success",
                "progress": progress
            }
        except Exception as e:
            logger.error(f"Ошибка при получении прогресса пользователя: {e}")
            return {
                "status": "error",
                "message": "Произошла ошибка при получении прогресса"
            }

    async def get_global_progress(self) -> Dict:
        """
        Получение глобального прогресса.
        
        Returns:
            Dict: Глобальный прогресс
        """
        try:
            # Получаем из базы данных
            async with self.db_manager.get_connection() as conn:
                # Общее количество пользователей
                async with conn.execute(
                    "SELECT COUNT(DISTINCT user_id) as total FROM learning_progress"
                ) as cursor:
                    total_users = (await cursor.fetchone())['total']

                # Активные пользователи
                async with conn.execute(
                    """
                    SELECT COUNT(DISTINCT user_id) as active
                    FROM learning_progress
                    WHERE timestamp >= datetime('now', '-1 day')
                    """
                ) as cursor:
                    active_users = (await cursor.fetchone())['active']

                # Средние метрики по курсам
                async with conn.execute(
                    """
                    SELECT course,
                           AVG(completion_rate) as avg_completion,
                           AVG(accuracy) as avg_accuracy,
                           SUM(time_spent) as total_time
                    FROM learning_progress
                    GROUP BY course
                    """
                ) as cursor:
                    course_metrics = await cursor.fetchall()

            # Получаем метрики из MLflow
            mlflow_metrics = self.mlflow_manager.get_latest_metrics("global_completion_rate", limit=1)

            progress = {
                "total_users": total_users,
                "active_users": active_users,
                "courses": {}
            }

            # Обрабатываем метрики курсов
            for row in course_metrics:
                course = row['course']
                progress['courses'][course] = {
                    "average_completion": row['avg_completion'] or 0.0,
                    "average_accuracy": row['avg_accuracy'] or 0.0,
                    "total_time": row['total_time'] or 0
                }

            # Обновляем глобальные метрики из MLflow
            if mlflow_metrics:
                progress['global_completion_rate'] = mlflow_metrics[0].get(
                    'metrics', {}
                ).get('completion_rate', 0.0)

            return {
                "status": "success",
                "progress": progress
            }
        except Exception as e:
            logger.error(f"Ошибка при получении глобального прогресса: {e}")
            return {
                "status": "error",
                "message": "Произошла ошибка при получении глобального прогресса"
            } 