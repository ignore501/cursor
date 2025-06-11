"""
Модуль для отслеживания эффективности команд бота.
"""
from typing import Dict, List, Optional
import logging
from datetime import datetime
from src.utils.database.db_manager import DatabaseManager
from src.utils.mlflow_manager import MLflowManager
from src.utils.metrics import Metrics

logger = logging.getLogger(__name__)

class CommandMetrics:
    """Класс для отслеживания эффективности команд."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Инициализация отслеживания команд.
        
        Args:
            db_manager: Менеджер базы данных
        """
        self.db_manager = db_manager
        self.mlflow_manager = MLflowManager()
        self.metrics = Metrics()
        self._initialized = False

    async def initialize(self) -> None:
        """Инициализация отслеживания команд."""
        if not self._initialized:
            try:
                async with self.db_manager.get_connection() as conn:
                    await conn.execute(
                        """
                        CREATE TABLE IF NOT EXISTS command_metrics (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            command TEXT NOT NULL,
                            user_id INTEGER NOT NULL,
                            duration REAL NOT NULL,
                            success BOOLEAN NOT NULL,
                            error_message TEXT,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                    await conn.commit()
                self._initialized = True
                logger.info("CommandMetrics успешно инициализирован")
            except Exception as e:
                logger.error(f"Ошибка при инициализации CommandMetrics: {e}")
                raise

    async def track_command(self, command: str, user_id: int, duration: float, success: bool, error_message: Optional[str] = None) -> Dict:
        """
        Отслеживание выполнения команды.
        
        Args:
            command: Название команды
            user_id: ID пользователя
            duration: Длительность выполнения
            success: Успешность выполнения
            error_message: Сообщение об ошибке
            
        Returns:
            Dict: Результат отслеживания
        """
        try:
            # Начинаем новый запуск в MLflow
            self.mlflow_manager.start_run(run_name=f"command_{command}_{user_id}")

            # Логируем метрики
            self.mlflow_manager.log_metrics({
                "duration": duration,
                "success": 1.0 if success else 0.0
            })

            # Логируем параметры
            self.mlflow_manager.log_parameters({
                "command": command,
                "user_id": str(user_id),
                "timestamp": datetime.now().isoformat()
            })

            # Обновляем Prometheus метрики
            self.metrics.log_command_metrics(command, duration)
            if not success:
                self.metrics.log_error_metrics(f"command_{command}_error")

            # Сохраняем в базу данных
            async with self.db_manager.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO command_metrics (
                        command, user_id, duration, success, error_message
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (command, user_id, duration, success, error_message)
                )
                await conn.commit()

            # Завершаем запуск
            self.mlflow_manager.end_run()

            return {
                "status": "success",
                "message": "Метрики команды успешно сохранены"
            }
        except Exception as e:
            logger.error(f"Ошибка при отслеживании команды: {e}")
            return {
                "status": "error",
                "message": "Произошла ошибка при сохранении метрик"
            }

    async def get_command_stats(self, command: str) -> Dict:
        """
        Получение статистики по команде.
        
        Args:
            command: Название команды
            
        Returns:
            Dict: Статистика команды
        """
        try:
            # Получаем из базы данных
            async with self.db_manager.get_connection() as conn:
                # Общее количество вызовов
                async with conn.execute(
                    "SELECT COUNT(*) as total FROM command_metrics WHERE command = ?",
                    (command,)
                ) as cursor:
                    total_calls = (await cursor.fetchone())['total']

                # Успешные вызовы
                async with conn.execute(
                    "SELECT COUNT(*) as success FROM command_metrics WHERE command = ? AND success = 1",
                    (command,)
                ) as cursor:
                    success_calls = (await cursor.fetchone())['success']

                # Средняя длительность
                async with conn.execute(
                    "SELECT AVG(duration) as avg_duration FROM command_metrics WHERE command = ?",
                    (command,)
                ) as cursor:
                    avg_duration = (await cursor.fetchone())['avg_duration'] or 0.0

                # Последние ошибки
                async with conn.execute(
                    """
                    SELECT error_message, timestamp
                    FROM command_metrics
                    WHERE command = ? AND success = 0
                    ORDER BY timestamp DESC
                    LIMIT 5
                    """,
                    (command,)
                ) as cursor:
                    recent_errors = await cursor.fetchall()

            # Получаем метрики из MLflow
            mlflow_metrics = self.mlflow_manager.get_latest_metrics(
                f"command_{command}_duration",
                limit=1
            )

            stats = {
                "total_calls": total_calls,
                "success_rate": (success_calls / total_calls * 100) if total_calls > 0 else 0.0,
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
            logger.error(f"Ошибка при получении статистики команды: {e}")
            return {
                "status": "error",
                "message": "Произошла ошибка при получении статистики"
            }

    async def get_user_command_stats(self, user_id: int) -> Dict:
        """
        Получение статистики команд пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict: Статистика команд пользователя
        """
        try:
            # Получаем из базы данных
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(
                    """
                    SELECT command,
                           COUNT(*) as total_calls,
                           SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_calls,
                           AVG(duration) as avg_duration
                    FROM command_metrics
                    WHERE user_id = ?
                    GROUP BY command
                    """,
                    (user_id,)
                ) as cursor:
                    command_stats = await cursor.fetchall()

            # Получаем метрики из MLflow
            mlflow_metrics = self.mlflow_manager.get_latest_metrics(
                f"user_{user_id}_command_duration",
                limit=10
            )

            stats = {
                "commands": {},
                "total_commands": 0,
                "success_rate": 0.0,
                "average_duration": 0.0
            }

            # Обрабатываем статистику команд
            total_calls = 0
            total_success = 0
            total_duration = 0.0

            for row in command_stats:
                command = row['command']
                stats['commands'][command] = {
                    "total_calls": row['total_calls'],
                    "success_rate": (row['success_calls'] / row['total_calls'] * 100) if row['total_calls'] > 0 else 0.0,
                    "average_duration": row['avg_duration'] or 0.0
                }

                total_calls += row['total_calls']
                total_success += row['success_calls']
                total_duration += (row['avg_duration'] or 0.0) * row['total_calls']

            if total_calls > 0:
                stats['total_commands'] = total_calls
                stats['success_rate'] = (total_success / total_calls * 100)
                stats['average_duration'] = total_duration / total_calls

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
            logger.error(f"Ошибка при получении статистики команд пользователя: {e}")
            return {
                "status": "error",
                "message": "Произошла ошибка при получении статистики"
            } 