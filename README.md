# Ronin - Telegram бот для обучения Data Science

Ronin - это Telegram бот, который помогает пользователям изучать Data Science через интерактивное обучение, практические задания и отслеживание прогресса.

## Возможности

- 📚 Структурированное обучение с планом
- 📊 Отслеживание прогресса
- 🎯 Практические задания
- 📈 Метрики и статистика
- 🤖 Интерактивное общение
- 📝 Голосование за темы
- ⭐ Система отзывов

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/ronin-tg-bot.git
cd ronin-tg-bot
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` и добавьте необходимые переменные окружения:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
DATABASE_URL=sqlite:///data/database.db
```

5. Инициализируйте pre-commit:
```bash
pre-commit install
```

## Запуск

```bash
python main.py
```

## Структура проекта

```
ronin-tg-bot/
├── data/
│   ├── database.db
│   ├── knowledge_base.json
│   ├── logs/
│   ├── plan.json
│   ├── settings.json
│   └── templates/
├── src/
│   ├── bot/
│   ├── database/
│   ├── learning/
│   ├── moderation/
│   └── utils/
├── tests/
├── .env
├── .pre-commit-config.yaml
├── main.py
├── README.md
└── requirements.txt
```

## Разработка

1. Создайте новую ветку для ваших изменений:
```bash
git checkout -b feature/your-feature-name
```

2. Внесите изменения и закоммитьте их:
```bash
git add .
git commit -m "feat: add new feature"
```

3. Отправьте изменения в репозиторий:
```bash
git push origin feature/your-feature-name
```

4. Создайте Pull Request

## Тестирование

```bash
pytest
```

## Лицензия

MIT

## Авторы

- Ваше имя - [GitHub](https://github.com/yourusername) 