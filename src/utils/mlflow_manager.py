"""
Модуль для работы с MLflow.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.utils.logger import setup_logger
import mlflow

logger = setup_logger(__name__)

class MLflowManager:
    """Менеджер для работы с MLflow."""

    def __init__(self, tracking_uri: str = "http://localhost:5000", experiment_name: str = "telegram_bot"):
        """Инициализация менеджера MLflow.
        
        Args:
            tracking_uri: URI для отслеживания экспериментов
            experiment_name: Название эксперимента
        """
        self.tracking_uri = tracking_uri
        self.experiment_name = experiment_name
        self._setup_mlflow()
        self._current_run = None

    def _setup_mlflow(self) -> None:
        """Настройка MLflow."""
        try:
            mlflow.set_tracking_uri(self.tracking_uri)
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(self.experiment_name)
            else:
                experiment_id = experiment.experiment_id
            mlflow.set_experiment(experiment_id)
            logger.info(f"MLflow настроен: {self.tracking_uri}, эксперимент: {self.experiment_name}")
        except Exception as e:
            logger.error(f"Ошибка при настройке MLflow: {e}")
            raise

    def start_run(self, run_name: Optional[str] = None) -> None:
        """Начало нового запуска.
        
        Args:
            run_name: Название запуска
        """
        try:
            if self._current_run is None:
                self._current_run = mlflow.start_run(run_name=run_name)
                logger.info(f"Начат новый запуск: {run_name or 'unnamed'}")
        except Exception as e:
            logger.error(f"Ошибка при начале запуска: {e}")
            raise

    def end_run(self) -> None:
        """Завершение текущего запуска."""
        try:
            if self._current_run is not None:
                mlflow.end_run()
                self._current_run = None
                logger.info("Запуск завершен")
        except Exception as e:
            logger.error(f"Ошибка при завершении запуска: {e}")
            raise

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        """Логирование метрик.
        
        Args:
            metrics: Словарь с метриками
            step: Шаг обучения
        """
        try:
            if self._current_run is None:
                self.start_run()
            
            for name, value in metrics.items():
                if isinstance(value, (int, float)):
                    mlflow.log_metric(name, float(value), step=step)
                else:
                    logger.warning(f"Пропущена метрика {name}: значение должно быть числовым")
            
            logger.info(f"Метрики залогированы: {metrics}")
        except Exception as e:
            logger.error(f"Ошибка при логировании метрик: {e}")
            raise

    def log_parameters(self, params: Dict[str, Any]) -> None:
        """Логирование параметров.
        
        Args:
            params: Словарь с параметрами
        """
        try:
            if self._current_run is None:
                self.start_run()
            
            mlflow.log_params(params)
            logger.info(f"Параметры залогированы: {params}")
        except Exception as e:
            logger.error(f"Ошибка при логировании параметров: {e}")
            raise

    def log_model(self, model: Any, name: str) -> None:
        """Логирование модели.
        
        Args:
            model: Модель для логирования
            name: Название модели
        """
        try:
            if self._current_run is None:
                self.start_run()
            
            mlflow.sklearn.log_model(model, name)
            logger.info(f"Модель залогирована: {name}")
        except Exception as e:
            logger.error(f"Ошибка при логировании модели: {e}")
            raise

    def log_notebook_metrics(self, notebook_path: str) -> None:
        """Логирование метрик из Jupyter ноутбука.
        
        Args:
            notebook_path: Путь к ноутбуку
        """
        try:
            from src.core.learning.notebook_parser import NotebookParser
            parser = NotebookParser()
            if metrics := parser.get_notebook_metrics(notebook_path):
                self.log_metrics(metrics)
                logger.info(f"Метрики из ноутбука залогированы: {metrics}")
        except Exception as e:
            logger.error(f"Ошибка при логировании метрик из ноутбука: {e}")
            raise

    def get_latest_metrics(self, metric_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение последних метрик.
        
        Args:
            metric_name: Название метрики
            limit: Количество последних значений
            
        Returns:
            Список словарей с метриками
        """
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                logger.warning(f"Эксперимент {self.experiment_name} не найден")
                return []

            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=f"metrics.{metric_name} != null",
                order_by=[f"metrics.{metric_name} DESC"],
                max_results=limit
            )
            
            if runs.empty:
                logger.warning(f"Метрика {metric_name} не найдена")
                return []
                
            return runs.to_dict('records')
        except Exception as e:
            logger.error(f"Ошибка при получении метрик: {e}")
            return []

    def get_best_run(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """Получение лучшего запуска по метрике.
        
        Args:
            metric_name: Название метрики
            
        Returns:
            Словарь с информацией о лучшем запуске
        """
        try:
            runs = self.get_latest_metrics(metric_name, limit=1)
            return runs[0] if runs else None
        except Exception as e:
            logger.error(f"Ошибка при получении лучшего запуска: {e}")
            return None 