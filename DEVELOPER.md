# Руководство разработчика

## Начало работы

1. Установите зависимости для разработки:
```bash
pip install -r requirements-dev.txt
```

2. Настройте pre-commit хуки:
```bash
pre-commit install
```

## Структура кода

### Основные компоненты

```
scripts/
├── autopost.py      # Основной скрипт бота
│   ├── KaggleLearningBot - Основной класс бота
│   ├── Команды и обработчики
│   └── Планировщик постов
├── database.py      # Работа с БД
│   ├── Database - Класс для работы с БД
│   ├── Асинхронные операции
│   └── Миграции
├── jupyter_parser.py # Парсинг Jupyter ноутбуков
│   ├── JupyterParser - Парсинг ноутбуков
│   ├── Извлечение метрик
│   └── Обработка кода
├── moderator.py     # Модерация сообщений
│   ├── Moderator - Модерация контента
│   ├── RateLimit - Ограничение частоты
│   └── Фильтры
├── post_templates.py # Шаблоны постов
│   ├── PostGenerator - Генерация постов
│   ├── Шаблоны
│   └── Форматирование
├── metrics.py       # Метрики и мониторинг
│   ├── Metrics - Метрики Prometheus
│   ├── Логирование
│   └── Декораторы
├── cache.py         # Работа с Redis
│   ├── Cache - Кеширование
│   ├── Операции с Redis
│   └── Декораторы
├── check.py         # Проверка кода
│   ├── Проверка безопасности
│   ├── Проверка типов
│   └── Форматирование
└── deploy.py        # Скрипт деплоя
    ├── Deployer - Управление деплоем
    ├── Бэкапы
    └── Проверки
```

### Тесты

```
tests/
├── __init__.py
├── conftest.py      # Конфигурация тестов
├── test_autopost.py # Тесты основного скрипта
├── test_bot.py      # Тесты бота
├── test_config.py   # Тесты конфигурации
├── test_database.py # Тесты БД
├── test_jupyter_parser.py # Тесты парсера
├── test_learning.py # Тесты обучения
├── test_moderator.py # Тесты модерации
├── test_post_templates.py # Тесты шаблонов
└── test_utils.py    # Тесты утилит
```

### Конфигурация

```
.
├── config.py         # Основные настройки
│   ├── Переменные окружения
│   ├── Пути
│   └── Константы
├── config.json      # Дополнительная конфигурация
├── .env            # Конфигурация окружения
├── .env.example    # Пример конфигурации
└── requirements.txt # Зависимости
```

### CI/CD

```
.github/
└── workflows/      # GitHub Actions
    ├── check.yml  # Проверка кода
    ├── test.yml   # Запуск тестов
    └── deploy.yml # Деплой
```

## Разработка

### Стиль кода

- Используйте [black](https://black.readthedocs.io/) для форматирования
- Сортируйте импорты с помощью [isort](https://pycqa.github.io/isort/)
- Проверяйте код с помощью [flake8](https://flake8.pycqa.org/)
- Используйте [mypy](https://mypy.readthedocs.io/) для проверки типов

### Тестирование

1. Запустите все тесты:
```bash
pytest
```

2. Запустите тесты с покрытием:
```bash
pytest --cov=scripts tests/
```

3. Запустите тесты с отчетом:
```bash
pytest --cov=scripts --cov-report=html tests/
```

### Проверка кода

Для проверки кода используйте скрипт `scripts/check.py`:

```bash
python scripts/check.py
```

Скрипт выполнит:
1. Проверку безопасности (safety, bandit)
2. Проверку типов (mypy)
3. Запуск тестов (pytest)
4. Проверку форматирования (black, isort, flake8)

## Деплой

### Подготовка к деплою

1. Создайте production конфигурацию:
```bash
cp .env.example .env.prod
```

2. Отредактируйте `.env.prod` с production значениями

### Процесс деплоя

1. Запустите скрипт деплоя:
```bash
python scripts/deploy.py
```

2. Проверьте логи:
```bash
docker logs -f ronin-tg-app
```

3. Проверьте метрики:
```bash
curl http://localhost:9090/metrics
```

## Мониторинг

### Метрики

Основные метрики доступны через Prometheus:

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

## Оптимизация

### Кеширование

Для кеширования используется Redis. Основные операции:

```python
from scripts.cache import cache

# Кеширование результата функции
@cache.cached(ttl=3600)
async def get_user_stats(user_id: int) -> dict:
    ...

# Ручное кеширование
await cache.set("key", value, ttl=3600)
value = await cache.get("key")
```

### Rate Limiting

Для ограничения частоты запросов используется rate limiting:

```python
from scripts.moderator import RateLimit

rate_limit = RateLimit(calls=5, period=60)

@rate_limit
async def handle_message(message):
    ...
```

## Безопасность

### Проверка безопасности

1. Проверка зависимостей:
```bash
safety check
```

2. Проверка кода:
```bash
bandit -r scripts/
```

### Рекомендации

1. Всегда используйте параметризованные запросы к БД
2. Валидируйте все входные данные
3. Используйте rate limiting для API endpoints
4. Храните секреты в переменных окружения
5. Регулярно обновляйте зависимости

## Отладка

### Локальная отладка

1. Запустите Redis:
```bash
redis-server
```

2. Запустите бота в режиме отладки:
```bash
python -m pdb scripts/autopost.py
```

### Логирование

Используйте структурированное логирование:

```python
import structlog

logger = structlog.get_logger()
logger.info("event_name", key=value)
```

## База знаний

### Структура

База знаний (`data/knowledge_base.json`) содержит структурированную информацию о Data Science в формате JSON:

```json
{
    "concepts": {
        "data_science": {
            "description": "Описание концепции",
            "key_points": ["Ключевые моменты"],
            "resources": ["Ссылки на ресурсы"]
        }
    },
    "tools": {
        "python": {
            "description": "Описание инструмента",
            "libraries": ["Список библиотек"],
            "resources": ["Ссылки на ресурсы"]
        }
    },
    "datasets": {
        "titanic": {
            "description": "Описание набора данных",
            "features": ["Особенности данных"],
            "url": "Ссылка на набор данных"
        }
    }
}
```

### Использование

База знаний используется в следующих компонентах:

1. **PostGenerator** (`scripts/post_templates.py`):
   - Генерация образовательного контента
   - Создание постов с информацией о концепциях
   - Рекомендации ресурсов

2. **JupyterParser** (`scripts/jupyter_parser.py`):
   - Связывание ноутбуков с концепциями
   - Добавление контекстной информации
   - Генерация описаний

3. **Moderator** (`scripts/moderator.py`):
   - Проверка релевантности контента
   - Фильтрация по темам
   - Рекомендации по улучшению

### Расширение

Для добавления новой информации в базу знаний:

1. Выберите подходящую категорию (concepts/tools/datasets)
2. Добавьте новый элемент с уникальным ключом
3. Заполните все обязательные поля:
   - description
   - key_points/features/libraries
   - resources/url

Пример:
```json
{
    "concepts": {
        "new_concept": {
            "description": "Описание новой концепции",
            "key_points": [
                "Ключевой момент 1",
                "Ключевой момент 2"
            ],
            "resources": [
                "https://example.com/resource1",
                "https://example.com/resource2"
            ]
        }
    }
}
```