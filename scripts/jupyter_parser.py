"""
Модуль для парсинга Jupyter ноутбуков и извлечения метрик, кода и графиков.
"""
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import mlflow
import nbformat
import pandas as pd
from nbconvert import PythonExporter

from config import EXPERIMENT_NAME, MLFLOW_TRACKING_URI, NOTEBOOKS_DIR

class JupyterParser:
    """Класс для парсинга Jupyter ноутбуков."""

    def __init__(self):
        """Инициализация парсера."""
        self.notebooks_dir = NOTEBOOKS_DIR
        self.python_exporter = PythonExporter()
        
        # Инициализация MLflow
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment(EXPERIMENT_NAME)

    def parse_notebook(self, notebook_path: Path) -> Dict:
        """
        Парсинг Jupyter ноутбука и извлечение информации.
        
        Args:
            notebook_path: Путь к ноутбуку
            
        Returns:
            Dict с извлеченной информацией
        """
        with open(notebook_path, "r", encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)
        
        # Извлечение информации
        cells = self._extract_cells(notebook)
        metrics = self._extract_metrics(cells)
        code_snippets = self._extract_code_snippets(cells)
        plots = self._extract_plots(cells)
        
        # Логирование метрик в MLflow
        with mlflow.start_run(run_name=f"notebook_{notebook_path.stem}"):
            for metric_name, value in metrics.items():
                mlflow.log_metric(metric_name, value)
            
            # Логирование кода
            mlflow.log_text("\n".join(code_snippets), "code_snippets.txt")
            
            # Логирование графиков
            for i, plot in enumerate(plots):
                mlflow.log_image(plot["image_data"], f"plot_{i}.png")
        
        return {
            "metrics": metrics,
            "code_snippets": code_snippets,
            "plots": plots,
            "summary": self._generate_summary(cells)
        }

    def _extract_cells(self, notebook: nbformat.NotebookNode) -> List[Dict]:
        """
        Извлечение содержимого ячеек ноутбука.
        
        Args:
            notebook: Объект ноутбука
            
        Returns:
            List[Dict] с содержимым ячеек
        """
        cells = []
        for cell in notebook.cells:
            if cell.cell_type == "code":
                cells.append({
                    "type": "code",
                    "source": cell.source,
                    "outputs": cell.outputs
                })
            elif cell.cell_type == "markdown":
                cells.append({
                    "type": "markdown",
                    "source": cell.source
                })
        return cells

    def _extract_metrics(self, cells: List[Dict]) -> Dict:
        """
        Извлечение метрик из ячеек.
        
        Args:
            cells: Список ячеек
            
        Returns:
            Dict с метриками
        """
        metrics = {}
        metric_patterns = {
            "accuracy": r"accuracy\s*=\s*([\d.]+)",
            "loss": r"loss\s*=\s*([\d.]+)",
            "f1": r"f1_score\s*=\s*([\d.]+)",
            "precision": r"precision\s*=\s*([\d.]+)",
            "recall": r"recall\s*=\s*([\d.]+)",
            "auc": r"auc\s*=\s*([\d.]+)",
            "rmse": r"rmse\s*=\s*([\d.]+)",
            "mae": r"mae\s*=\s*([\d.]+)",
            "r2": r"r2_score\s*=\s*([\d.]+)",
        }
        
        for cell in cells:
            if cell["type"] == "code":
                # Поиск метрик в коде
                for metric_name, pattern in metric_patterns.items():
                    matches = re.findall(pattern, cell["source"], re.IGNORECASE)
                    if matches:
                        metrics[metric_name] = float(matches[-1])
                
                # Поиск метрик в выводах ячеек
                for output in cell.get("outputs", []):
                    if "text" in output:
                        for metric_name, pattern in metric_patterns.items():
                            matches = re.findall(pattern, output["text"], re.IGNORECASE)
                            if matches:
                                metrics[metric_name] = float(matches[-1])
        
        return metrics

    def _extract_code_snippets(self, cells: List[Dict]) -> List[str]:
        """
        Извлечение полезных сниппетов кода.
        
        Args:
            cells: Список ячеек
            
        Returns:
            List[str] со сниппетами кода
        """
        snippets = []
        for cell in cells:
            if cell["type"] == "code":
                # Проверка на наличие полезных комментариев
                if "# TODO" in cell["source"] or "# FIXME" in cell["source"]:
                    continue
                
                # Извлечение кода без вывода
                code = cell["source"].strip()
                if code and not code.startswith("%"):
                    # Добавление комментариев к коду
                    comments = re.findall(r"#\s*(.+)$", code, re.MULTILINE)
                    if comments:
                        code = f"# {' | '.join(comments)}\n{code}"
                    snippets.append(code)
        
        return snippets

    def _extract_plots(self, cells: List[Dict]) -> List[Dict]:
        """
        Извлечение информации о графиках.
        
        Args:
            cells: Список ячеек
            
        Returns:
            List[Dict] с информацией о графиках
        """
        plots = []
        for cell in cells:
            if cell["type"] == "code":
                for output in cell.get("outputs", []):
                    if "data" in output and "image/png" in output["data"]:
                        # Извлечение заголовка графика
                        title = None
                        if "text" in output:
                            title_match = re.search(r"title\s*=\s*['\"](.+?)['\"]", output["text"])
                            if title_match:
                                title = title_match.group(1)
                        
                        plots.append({
                            "cell_source": cell["source"],
                            "image_data": output["data"]["image/png"],
                            "title": title
                        })
        return plots

    def _generate_summary(self, cells: List[Dict]) -> str:
        """
        Генерация краткого описания ноутбука.
        
        Args:
            cells: Список ячеек
            
        Returns:
            str с описанием
        """
        summary_parts = []
        
        # Извлечение заголовков из markdown ячеек
        for cell in cells:
            if cell["type"] == "markdown":
                headers = re.findall(r"^#+\s+(.+)$", cell["source"], re.MULTILINE)
                if headers:
                    summary_parts.extend(headers)
        
        return " | ".join(summary_parts)

    def get_latest_notebook(self) -> Optional[Path]:
        """
        Получение пути к последнему измененному ноутбуку.
        
        Returns:
            Optional[Path] путь к ноутбуку
        """
        notebooks = list(self.notebooks_dir.glob("*.ipynb"))
        if not notebooks:
            return None
        
        return max(notebooks, key=lambda p: p.stat().st_mtime)

    def get_notebook_metrics(self, notebook_path: Path) -> pd.DataFrame:
        """
        Получение метрик из ноутбука в виде DataFrame.
        
        Args:
            notebook_path: Путь к ноутбуку
            
        Returns:
            pd.DataFrame с метриками
        """
        notebook_data = self.parse_notebook(notebook_path)
        metrics = notebook_data["metrics"]
        
        return pd.DataFrame([metrics])

    def get_metrics_history(self, days: int = 7) -> pd.DataFrame:
        """
        Получение истории метрик за последние дни.
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            pd.DataFrame с историей метрик
        """
        start_date = datetime.now() - pd.Timedelta(days=days)
        
        # Получение всех запусков за период
        runs = mlflow.search_runs(
            experiment_names=[EXPERIMENT_NAME],
            filter_string=f"start_time >= '{start_date}'"
        )
        
        if runs.empty:
            return pd.DataFrame()
        
        # Извлечение метрик
        metrics_df = runs[["metrics.accuracy", "metrics.loss", "metrics.f1"]].copy()
        metrics_df.index = pd.to_datetime(runs["start_time"])
        metrics_df.sort_index(inplace=True)
        
        return metrics_df 