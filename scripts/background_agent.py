import os
import time
import json
import logging
from github import Github
from datetime import datetime
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackgroundAgent:
    def __init__(self):
        # Сначала пробуем получить настройки из config.json
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                self.github_token = config.get("github", {}).get("token")
                self.repository = config.get("github", {}).get("repository")
                self.owner = config.get("github", {}).get("owner")
        
        # Если не нашли в config.json, берем из переменных окружения
        if not all([self.github_token, self.repository, self.owner]):
            self.github_token = os.getenv('GITHUB_TOKEN')
            self.repository = os.getenv('GITHUB_REPOSITORY', '').split('/')[-1]
            self.owner = os.getenv('GITHUB_OWNER')
        
        if not all([self.github_token, self.repository, self.owner]):
            raise ValueError("Missing required GitHub configuration. Please check config.json or environment variables.")
            
        try:
            self.github = Github(self.github_token)
            self.repo = self.github.get_repo(f"{self.owner}/{self.repository}")
            logger.info(f"Initialized GitHub connection for {self.owner}/{self.repository}")
        except Exception as e:
            logger.error(f"Failed to initialize GitHub connection: {e}")
            raise
            
    def check_repository_access(self):
        """Проверяет доступ к репозиторию"""
        try:
            self.repo.get_contents("")
            logger.info("Successfully connected to repository")
            return True
        except Exception as e:
            logger.error(f"Failed to access repository: {e}")
            return False
            
    def monitor_changes(self):
        """Мониторит изменения в репозитории"""
        try:
            # Получаем последний коммит
            commits = self.repo.get_commits()
            last_commit = commits[0]
            
            logger.info(f"Last commit: {last_commit.sha} by {last_commit.author.login}")
            
            # Проверяем изменения в последнем коммите
            files_changed = last_commit.files
            for file in files_changed:
                logger.info(f"Changed file: {file.filename}")
                
                # Здесь можно добавить специфическую логику для разных типов файлов
                if file.filename.endswith('.py'):
                    logger.info(f"Python file changed: {file.filename}")
                elif file.filename.endswith('.yml') or file.filename.endswith('.yaml'):
                    logger.info(f"Config file changed: {file.filename}")
            
        except Exception as e:
            logger.error(f"Error monitoring changes: {e}")
            
    def run(self):
        """Запускает агента"""
        if not self.check_repository_access():
            logger.error("Failed to start background agent due to repository access issues")
            return
            
        logger.info("Starting background agent")
        
        while True:
            try:
                self.monitor_changes()
                time.sleep(60)  # Проверка каждую минуту
            except KeyboardInterrupt:
                logger.info("Stopping background agent")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(60)  # Пауза перед следующей попыткой

if __name__ == "__main__":
    try:
        agent = BackgroundAgent()
        agent.run()
    except Exception as e:
        logger.error(f"Failed to start background agent: {e}")
        exit(1) 