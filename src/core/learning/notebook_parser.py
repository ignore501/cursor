"""
Модуль для парсинга Jupyter ноутбуков.
"""

import contextlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from src.utils.logger import setup_logger
import nbformat
from nbconvert import HTMLExporter, PythonExporter
from src.utils.mlflow_manager import MLflowManager
from datetime import datetime
from src.utils.database.db_manager import DatabaseManager
from src.core.learning.learning_metrics import LearningMetrics

logger = setup_logger(__name__)

class NotebookParser:
    """Парсер Jupyter ноутбуков."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Инициализация парсера.
        
        Args:
            db_manager: Менеджер базы данных
        """
        self.db_manager = db_manager
        self.learning_metrics = LearningMetrics(db_manager) if db_manager else None
        self._initialized = False
        self.notebooks_dir = None
        self.exporter = HTMLExporter()
        self.python_exporter = PythonExporter()
        self.mlflow_manager = MLflowManager()
        self._cache: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self) -> None:
        """Инициализация парсера"""
        if not self._initialized and self.db_manager:
            try:
                await self.learning_metrics.initialize()
                self._initialized = True
                logger.info("NotebookParser успешно инициализирован")
            except Exception as e:
                logger.error(f"Ошибка при инициализации NotebookParser: {e}")
                raise

    def parse_notebook(self, notebook: Union[str, Path, Dict]) -> Dict:
        """Парсинг ноутбука.
        
        Args:
            notebook: Путь к ноутбуку или его содержимое
            
        Returns:
            Dict: Словарь с данными ноутбука
        """
        try:
            if isinstance(notebook, (str, Path)):
                notebook = nbformat.read(notebook, as_version=4)
            
            # Начинаем новый запуск в MLflow
            self.mlflow_manager.start_run(run_name=f"notebook_parse_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Извлекаем метрики
            metrics = self._extract_metrics(notebook.cells)
            if metrics:
                self.mlflow_manager.log_metrics(metrics)
            
            # Извлекаем код
            code = self._extract_code(notebook.cells)
            
            # Извлекаем графики
            plots = self._extract_plots(notebook.cells)
            
            # Генерируем сводку
            summary = self._generate_summary(notebook.cells)
            
            # Логируем параметры
            self.mlflow_manager.log_parameters({
                'notebook_name': notebook.metadata.get('name', 'unnamed'),
                'cell_count': len(notebook.cells),
                'code_cell_count': len([c for c in notebook.cells if c.cell_type == 'code']),
                'markdown_cell_count': len([c for c in notebook.cells if c.cell_type == 'markdown'])
            })
            
            # Завершаем запуск
            self.mlflow_manager.end_run()
            
            return {
                'cells': notebook.cells,
                'metadata': notebook.metadata,
                'metrics': metrics,
                'code': code,
                'plots': plots,
                'summary': summary
            }
        except Exception as e:
            logger.error(f"Ошибка при парсинге ноутбука: {e}")
            return {}

    def _extract_metrics(self, cells: List[Dict]) -> Dict[str, float]:
        """Извлечение метрик из ячеек ноутбука.
        
        Args:
            cells: Список ячеек ноутбука
            
        Returns:
            Dict[str, float]: Словарь с метриками
        """
        metrics = {}
        for cell in cells:
            if cell.get('cell_type') == 'code':
                source = ''.join(cell.get('source', []))
                # Ищем метрики в коде
                if 'accuracy' in source:
                    with contextlib.suppress(Exception):
                        metrics['accuracy'] = float(source.split('accuracy')[1].split('=')[1].split()[0])
                if 'f1' in source:
                    with contextlib.suppress(Exception):
                        metrics['f1'] = float(source.split('f1')[1].split('=')[1].split()[0])
                if 'loss' in source:
                    with contextlib.suppress(Exception):
                        metrics['loss'] = float(source.split('loss')[1].split('=')[1].split()[0])
        return metrics

    def _extract_code(self, cells: List[Dict]) -> List[str]:
        """Извлечение кода из ячеек ноутбука.
        
        Args:
            cells: Список ячеек ноутбука
            
        Returns:
            List[str]: Список кода
        """
        code = []
        for cell in cells:
            if cell.get('cell_type') == 'code':
                source = ''.join(cell.get('source', []))
                if source.strip():
                    code.append(source)
        return code

    def _extract_plots(self, cells: List[Dict]) -> List[Dict]:
        """Извлечение графиков из ячеек ноутбука.
        
        Args:
            cells: Список ячеек ноутбука
            
        Returns:
            List[Dict]: Список графиков
        """
        plots = []
        for cell in cells:
            if cell.get('cell_type') == 'code':
                outputs = cell.get('outputs', [])
                plots.extend(
                    output['data']
                    for output in outputs
                    if isinstance(output, dict)
                    and 'data' in output
                    and 'image/png' in output['data']
                )
        return plots

    def _generate_summary(self, cells: List[Dict]) -> str:
        """Генерация сводки из ячеек ноутбука.
        
        Args:
            cells: Список ячеек ноутбука
            
        Returns:
            str: Сводка
        """
        summary = []
        for cell in cells:
            if cell.get('cell_type') == 'markdown':
                source = ''.join(cell.get('source', []))
                summary.append(source)
        return '\n'.join(summary)

    def get_latest_notebook(self) -> Optional[Path]:
        """Получение последнего ноутбука.
        
        Returns:
            Optional[Path]: Путь к последнему ноутбуку
        """
        if not self.notebooks_dir:
            return None
        notebooks = list(self.notebooks_dir.glob('*.ipynb'))
        return max(notebooks, key=lambda x: x.stat().st_mtime) if notebooks else None

    def get_notebook_metrics(self, notebook: Union[str, Path, Dict]) -> Dict:
        """Получение метрик из ноутбука.
        
        Args:
            notebook: Путь к ноутбуку или его содержимое
            
        Returns:
            Dict: Словарь с метриками
        """
        result = self.parse_notebook(notebook)
        return result.get('metrics', {})

    def convert_to_html(self, notebook: Union[str, Path, Dict]) -> str:
        """Конвертация ноутбука в HTML.
        
        Args:
            notebook: Путь к ноутбуку или его содержимое
            
        Returns:
            str: HTML представление ноутбука
        """
        if isinstance(notebook, (str, Path)):
            notebook = nbformat.read(notebook, as_version=4)
        return self.exporter.from_notebook_node(notebook)[0]

    async def get_today_summary(self) -> str:
        """Получение сводки за сегодня.
        
        Returns:
            str: Сводка
        """
        notebooks = self.get_today_notebooks()
        if not notebooks:
            return "Нет данных за сегодня"

        summaries = []
        for notebook in notebooks:
            if data := self.parse_notebook(notebook):
                summary = self._generate_summary(data['cells'])
                summaries.append(f"📊 {notebook.stem}:\n{summary}")

        return "\n\n".join(summaries) if summaries else "Нет данных за сегодня"

    def get_today_notebooks(self) -> List[Path]:
        """Получение ноутбуков за сегодня.
        
        Returns:
            List[Path]: Список путей к ноутбукам
        """
        if not self.notebooks_dir:
            return []

        today = datetime.now().date()
        notebooks = []

        notebooks.extend(
            notebook
            for notebook in self.notebooks_dir.glob('*.ipynb')
            if datetime.fromtimestamp(notebook.stat().st_mtime).date() == today
        )
        return notebooks 