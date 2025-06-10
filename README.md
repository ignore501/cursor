# Ronin Telegram Bot

Telegram бот для автоматизации постов о прогрессе обучения Data Science.

## Возможности

- Автоматическая публикация утренних и вечерних постов
- Система голосования за темы для изучения
- Модерация сообщений
- Отслеживание прогресса обучения
- Интеграция с MLflow для метрик
- Кеширование и оптимизация производительности
- Мониторинг и метрики

## Требования

- Python 3.10+
- Redis
- Docker (опционально)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/ronin-tg-app.git
cd ronin-tg-app
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл конфигурации:
```bash
cp .env.example .env
```

5. Отредактируйте `.env` файл, добавив необходимые переменные окружения:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
CHANNEL_ID=your_channel_id
MLFLOW_TRACKING_URI=http://localhost:5000
REDIS_URL=redis://localhost
```

## Запуск

### Локальный запуск

1. Запустите Redis:
```bash
redis-server
```

2. Запустите бота:
```bash
python scripts/autopost.py
```

### Запуск в Docker

1. Соберите Docker образ:
```bash
docker build -t ronin-tg-app:latest .
```

2. Запустите контейнер:
```bash
docker run -d \
  --name ronin-tg-app \
  -p 8080:8080 \
  -p 9090:9090 \
  --env-file .env \
  --restart unless-stopped \
  ronin-tg-app:latest
```

## Деплой

Для деплоя используйте скрипт `scripts/deploy.py`:

```bash
python scripts/deploy.py
```

Скрипт выполнит следующие действия:
1. Проверка окружения
2. Создание бэкапа базы данных
3. Сборка Docker образа
4. Остановка и удаление старого контейнера
5. Запуск нового контейнера
6. Проверка здоровья приложения

## Мониторинг

### Метрики

Метрики доступны по адресу: `http://localhost:9090/metrics`

Основные метрики:
- `bot_messages_total` - общее количество сообщений
- `bot_commands_total` - количество команд по типам
- `bot_errors_total` - количество ошибок по типам
- `message_processing_seconds` - время обработки сообщений
- `command_processing_seconds` - время обработки команд
- `database_operation_seconds` - время операций с БД

### Логи

Логи доступны в следующих местах:
- Файл: `logs/bot.log`
- Docker: `docker logs ronin-tg-app`

## Проверка кода

Для проверки кода используйте скрипт `scripts/check.py`:

```bash
python scripts/check.py
```

Скрипт выполнит:
1. Проверку безопасности (safety, bandit)
2. Проверку типов (mypy)
3. Запуск тестов (pytest)
4. Проверку форматирования (black, isort, flake8)

## Структура проекта

```
ronin-tg-app/
├── scripts/
│   ├── autopost.py      # Основной скрипт бота
│   ├── database.py      # Работа с БД
│   ├── jupyter_parser.py # Парсинг Jupyter ноутбуков
│   ├── moderator.py     # Модерация сообщений
│   ├── post_templates.py # Шаблоны постов
│   ├── metrics.py       # Метрики и мониторинг
│   ├── cache.py         # Работа с Redis
│   ├── check.py         # Проверка кода
│   └── deploy.py        # Скрипт деплоя
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Конфигурация тестов
│   ├── test_autopost.py # Тесты основного скрипта
│   ├── test_bot.py      # Тесты бота
│   ├── test_config.py   # Тесты конфигурации
│   ├── test_database.py # Тесты БД
│   ├── test_jupyter_parser.py # Тесты парсера
│   ├── test_learning.py # Тесты обучения
│   ├── test_moderator.py # Тесты модерации
│   ├── test_post_templates.py # Тесты шаблонов
│   └── test_utils.py    # Тесты утилит
├── data/               # Данные
│   └── knowledge_base.json # База знаний по Data Science
├── logs/               # Логи
├── .github/           # GitHub Actions
├── venv/              # Виртуальное окружение
├── .env              # Конфигурация окружения
├── .env.example      # Пример конфигурации
├── .dockerignore     # Исключения для Docker
├── .gitignore        # Исключения для Git
├── .pre-commit-config.yaml # Конфигурация pre-commit
├── config.py         # Конфигурация
├── config.json       # Дополнительная конфигурация
├── requirements.txt  # Зависимости
├── Dockerfile        # Конфигурация Docker
├── README.md         # Документация
├── DEVELOPER.md      # Руководство разработчика
└── tz.md            # Документация по часовым поясам
```

## База знаний

Бот использует базу знаний (`data/knowledge_base.json`) для предоставления информации о Data Science. База знаний содержит:

1. **Концепции** (`concepts`):
   - Data Science
   - Machine Learning
   - Feature Engineering
   - Описания, ключевые моменты и ресурсы для изучения

2. **Инструменты** (`tools`):
   - Python и основные библиотеки
   - Jupyter Notebook
   - Описания и ресурсы

3. **Наборы данных** (`datasets`):
   - Titanic
   - Iris
   - Описания и ссылки

База знаний используется для:
- Генерации образовательного контента
- Ответов на вопросы пользователей
- Рекомендации ресурсов для изучения
- Структурирования учебного процесса

## Лицензия

MIT 