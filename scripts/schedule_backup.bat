@echo off
REM Скрипт для запуска бэкапа базы данных
REM Запускается через планировщик задач Windows

REM Активация виртуального окружения
call venv\Scripts\activate.bat

REM Запуск скрипта бэкапа
python scripts/backup_db.py --max-backups 3

REM Деактивация виртуального окружения
deactivate 