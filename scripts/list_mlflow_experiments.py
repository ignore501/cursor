"""
Скрипт для вывода всех экспериментов и запусков в MLflow.
"""

import mlflow
from mlflow.tracking import MlflowClient

if __name__ == "__main__":
    print("Эксперименты в MLflow:")
    client = MlflowClient()
    experiments = client.search_experiments()
    for exp in experiments:
        print(f"- {exp.experiment_id}: {exp.name} (lifecycle: {exp.lifecycle_stage})")
        if runs := client.search_runs([exp.experiment_id], max_results=5):
            for run in runs:
                print(f"  Run {run.info.run_id}: status={run.info.status}, metrics={run.data.metrics}, params={run.data.params}") 
        else:
            print("  Нет запусков.") 