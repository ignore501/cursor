"""
Тестовый скрипт для проверки работы MLflow.
"""
import mlflow
from src.utils.mlflow_manager import MLflowManager
from src.config.config import Config

def test_mlflow_integration():
    """Тест интеграции с MLflow."""
    # Инициализация MLflow
    config = Config(
        TELEGRAM_TOKEN="test_token",
        telegram_channel_id="test_channel",
        kaggle_username="test_user",
        kaggle_key="test_key",
        competition_id="test_competition",
        telegram_bot_token="test_bot_token"
    )

    mlflow_manager = MLflowManager()

    try:
        _extracted_from_test_mlflow_integration_17(mlflow_manager)
    finally:
        # Завершение запуска
        mlflow_manager.end_run()


# TODO Rename this here and in `test_mlflow_integration`
def _extracted_from_test_mlflow_integration_17(mlflow_manager):
    # Начало нового запуска
    mlflow_manager.start_run(run_name="test_run")

    # Тестовые метрики
    metrics = {
        "accuracy": 0.95,
        "loss": 0.05,
        "f1_score": 0.94
    }

    # Логирование метрик
    mlflow_manager.log_metrics(metrics)

    # Логирование параметров
    params = {
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 10
    }
    mlflow_manager.log_parameters(params)

    # Получение последних метрик
    latest_metrics = mlflow_manager.get_latest_metrics("accuracy")
    print(f"Latest accuracy metrics: {latest_metrics}")

    # Получение лучшего запуска
    best_run = mlflow_manager.get_best_run("accuracy")
    print(f"Best run: {best_run}")

if __name__ == "__main__":
    test_mlflow_integration() 