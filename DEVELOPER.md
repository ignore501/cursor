# Руководство разработчика

## Содержание
1. [Начало работы](#начало-работы)
2. [Структура кода](#структура-кода)
3. [Разработка](#разработка)
4. [Тестирование](#тестирование)
5. [Деплой](#деплой)
6. [Мониторинг](#мониторинг)
7. [Оптимизация](#оптимизация)
8. [Безопасность](#безопасность)
9. [Отладка](#отладка)

## Начало работы

### Предварительные требования
- Python 3.10+
- Docker и Docker Compose
- Redis
- Git

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/ronin-tg-app.git
cd ronin-tg-app
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements-dev.txt
```

4. Настройте pre-commit хуки:
```bash
pre-commit install
```

5. Создайте файл .env:
```bash
cp .env.example .env
```

## Структура кода

### Основные компоненты

```
src/
├── bot/                    # Основной модуль бота
│   ├── handlers/          # Обработчики команд
│   └── main.py           # Точка входа
├── core/                  # Основная логика
│   ├── posts/            # Управление постами
│   ├── learning/         # Работа с ноутбуками
│   └── moderation/       # Модерация и голосования
├── utils/                # Вспомогательные функции
│   ├── templates/        # Шаблоны постов
│   ├── database/         # Работа с БД
│   └── summarizer/       # Суммаризация текста
└── ui/                   # Пользовательский интерфейс
    ├── keyboards/        # Клавиатуры
    └── messages/         # Шаблоны сообщений
```

### Тесты

```
tests/
├── __init__.py
├── conftest.py           # Конфигурация тестов
├── test_autopost.py      # Тесты основного скрипта
├── test_bot.py           # Тесты бота
├── test_config.py        # Тесты конфигурации
├── test_database.py      # Тесты БД
├── test_jupyter_parser.py # Тесты парсера
├── test_learning.py      # Тесты обучения
├── test_moderator.py     # Тесты модерации
├── test_post_templates.py # Тесты шаблонов
└── test_utils.py         # Тесты утилит
```

## Разработка

### Стиль кода

- Используйте [black](https://black.readthedocs.io/) для форматирования
- Сортируйте импорты с помощью [isort](https://pycqa.github.io/isort/)
- Проверяйте код с помощью [flake8](https://flake8.pycqa.org/)
- Используйте [mypy](https://mypy.readthedocs.io/) для проверки типов

### Рабочий процесс

1. Создайте новую ветку для задачи:
```bash
git checkout -b feature/your-feature-name
```

2. Внесите изменения и закоммитьте:
```bash
git add .
git commit -m "feat: add new feature"
```

3. Запушьте изменения:
```bash
git push origin feature/your-feature-name
```

4. Создайте Pull Request

### Локальная разработка

1. Запустите Redis:
```bash
docker run -d -p 6379:6379 redis
```

2. Запустите MLflow:
```bash
mlflow server --host 0.0.0.0
```

3. Запустите бота в режиме разработки:
```bash
python src/main.py --dev
```

## Тестирование

### Запуск тестов

1. Запустите все тесты:
```bash
pytest
```

2. Запустите тесты с покрытием:
```bash
pytest --cov=src tests/
```

3. Запустите тесты с отчетом:
```bash
pytest --cov=src --cov-report=html tests/
```

### Написание тестов

1. Создайте новый файл теста в директории `tests/`
2. Используйте фикстуры из `conftest.py`
3. Следуйте паттерну AAA (Arrange-Act-Assert)

Пример:
```python
def test_post_generation():
    # Arrange
    generator = PostGenerator()
    
    # Act
    post = generator.generate_morning_post()
    
    # Assert
    assert post is not None
    assert len(post) > 0
```

## Деплой

### Подготовка к деплою

1. Создайте production конфигурацию:
```bash
cp .env.example .env.prod
```

2. Отредактируйте `.env.prod` с production значениями

### Процесс деплоя

1. Соберите Docker образ:
```bash
docker build -t ronin-tg-app:latest .
```

2. Запустите контейнер:
```bash
docker run -d --env-file .env.prod ronin-tg-app:latest
```

3. Проверьте логи:
```bash
docker logs -f ronin-tg-app
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
from utils.cache import cache

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
from core.moderation import RateLimit

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
bandit -r src/
```

### Рекомендации

1. Всегда используйте параметризованные запросы к БД
2. Валидируйте все входные данные
3. Используйте rate limiting для API endpoints
4. Храните секреты в переменных окружения
5. Регулярно обновляйте зависимости

## Отладка

### Локальная отладка

1. Включите режим отладки:
```bash
export DEBUG=1
```

2. Используйте логирование:
```python
import logging

logging.debug("Debug message")
logging.info("Info message")
logging.warning("Warning message")
logging.error("Error message")
```

3. Используйте pdb для отладки:
```python
import pdb; pdb.set_trace()
```

### Профилирование

1. Запустите профилирование:
```bash
python -m cProfile -o output.prof src/main.py
```

2. Анализируйте результаты:
```bash
python -m pstats output.prof
```