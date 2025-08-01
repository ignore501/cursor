# Инструкция по настройке автоматического бэкапа

## Описание

Система автоматического бэкапа создает резервные копии базы данных с заданной периодичностью и хранит только последние N копий. Все бэкапы сохраняются в директории `backups/` с временными метками.

## Компоненты

1. `scripts/backup_db.py` - основной скрипт создания бэкапа
2. `scripts/schedule_backup.bat` - скрипт для запуска через планировщик задач Windows
3. `scripts/db_backup.service` - systemd сервис для Linux
4. `scripts/install_backup_service.sh` - скрипт установки systemd сервиса
5. `scripts/install_backup_cron.sh` - скрипт установки cron задачи
6. `logs/backup.log` - лог-файл с информацией о созданных бэкапах

## Ручной запуск

Для создания бэкапа вручную выполните:

```bash
python scripts/backup_db.py --max-backups 3
```

Параметры:
- `--db-path` - путь к файлу базы данных (по умолчанию: bot.db)
- `--max-backups` - максимальное количество хранимых бэкапов (по умолчанию: 3)

## Настройка в Windows

### Через планировщик задач

1. Откройте "Планировщик задач" (Task Scheduler)
2. Нажмите "Создать задачу" (Create Task)
3. На вкладке "Общие" (General):
   - Введите имя задачи (например, "Database Backup")
   - Выберите "Выполнять независимо от входа пользователя" (Run whether user is logged on or not)
   - Отметьте "Выполнять с наивысшими правами" (Run with highest privileges)

4. На вкладке "Триггеры" (Triggers):
   - Нажмите "Создать" (New)
   - Выберите "Ежедневно" (Daily)
   - Установите время (например, 00:00)
   - Нажмите OK

5. На вкладке "Действия" (Actions):
   - Нажмите "Создать" (New)
   - В поле "Действие" (Action) выберите "Запуск программы" (Start a program)
   - В поле "Программа/скрипт" (Program/script) укажите полный путь к `scripts/schedule_backup.bat`
   - В поле "Рабочая папка" (Start in) укажите путь к корневой директории проекта
   - Нажмите OK

6. Нажмите OK для сохранения задачи

## Настройка в Linux

### Через systemd

1. Скопируйте файл сервиса:
```bash
sudo cp scripts/db_backup.service /etc/systemd/system/
```

2. Установите права:
```bash
sudo chmod 644 /etc/systemd/system/db_backup.service
```

3. Перезагрузите systemd:
```bash
sudo systemctl daemon-reload
```

4. Включите и запустите сервис:
```bash
sudo systemctl enable db_backup.service
sudo systemctl start db_backup.service
```

Или используйте скрипт установки:
```bash
sudo bash scripts/install_backup_service.sh
```

### Через cron

1. Установите cron задачу:
```bash
sudo bash scripts/install_backup_cron.sh
```

Это создаст задачу, которая будет запускаться каждый день в 00:00.

## Проверка работы

1. Проверьте создание бэкапа:
   - Запустите скрипт вручную
   - Проверьте директорию `backups/`
   - Проверьте лог-файл `logs/backup.log`

2. Проверьте автоматический запуск:
   - Дождитесь времени запуска по расписанию
   - Проверьте создание нового бэкапа
   - Проверьте лог-файл

## Устранение неполадок

### Windows

1. Если бэкап не создается:
   - Проверьте права доступа к директориям `backups/` и `logs/`
   - Проверьте наличие файла базы данных
   - Проверьте лог-файл на наличие ошибок

2. Если автоматический запуск не работает:
   - Проверьте настройки планировщика задач
   - Проверьте путь к скрипту в планировщике
   - Проверьте права доступа к скрипту

### Linux

1. Проверка systemd сервиса:
```bash
sudo systemctl status db_backup.service
sudo journalctl -u db_backup.service
```

2. Проверка cron задачи:
```bash
sudo crontab -u ronin -l
```

3. Проверка логов:
```bash
tail -f logs/backup.log
tail -f logs/backup.error.log
```

## Рекомендации

1. Храните бэкапы в безопасном месте
2. Регулярно проверяйте лог-файл
3. Периодически тестируйте восстановление из бэкапа
4. Настройте уведомления об ошибках
5. Для Linux рекомендуется использовать systemd для более надежного управления сервисом 