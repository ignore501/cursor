# Telegram Bot для отслеживания прогресса в Data Science

Бот для автоматизации ведения Telegram-канала, отражающего прогресс обучения Data Science через участие в соревнованиях Kaggle. Проект использует современные технологии машинного обучения и автоматизации для создания качественного контента.

## Основные возможности

- 🤖 Автоматическая генерация утренних и вечерних постов
- 📊 Интеграция с Jupyter ноутбуками для извлечения метрик и кода
- 🗳️ Система голосования для выбора тем
- 📈 Отслеживание прогресса обучения через MLflow
- ⏰ Автоматическая публикация постов по расписанию
- 🔍 Интеллектуальная суммаризация контента с помощью BART
- 💾 Кеширование и оптимизация производительности
- 📝 Система модерации и фильтрации контента

## Технологический стек

- Python 3.10+
- python-telegram-bot
- Hugging Face Transformers (BART)
- MLflow для трекинга экспериментов
- Redis для кеширования
- Docker для контейнеризации
- Prometheus + Grafana для мониторинга

## Структура проекта

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

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/ronin-tg-app.git
cd ronin-tg-app
```

2. Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
pip install -r requirements.txt
```

3. Создайте файл .env с необходимыми переменными окружения:
```env
TELEGRAM_TOKEN=your_bot_token
REDIS_URL=redis://localhost:6379
MLFLOW_TRACKING_URI=http://localhost:5000
```

4. Запустите Redis (требуется для кеширования):
```bash
docker run -d -p 6379:6379 redis
```

## Запуск

1. Запустите бота:
```bash
python src/main.py
```

2. Для запуска в Docker:
```bash
docker build -t ronin-tg-app .
docker run -d --env-file .env ronin-tg-app
```

## Разработка

1. Установите зависимости для разработки:
```bash
pip install -r requirements-dev.txt
```

2. Настройте pre-commit хуки:
```bash
pre-commit install
```

3. Запустите тесты:
```bash
pytest
```

## Мониторинг

- Метрики доступны через Prometheus: `http://localhost:9090/metrics`
- Логи хранятся в `logs/bot.log`
- MLflow dashboard: `http://localhost:5000`

## Лицензия

MIT

## Поддержка

При возникновении проблем создавайте issue в репозитории проекта.