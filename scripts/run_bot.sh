#!/bin/bash

# Создаем директорию для логов если её нет
mkdir -p logs

# Запускаем бота в фоновом режиме с перенаправлением вывода в лог
nohup python3 scripts/autopost.py > logs/bot.log 2>&1 &

# Сохраняем PID бота
echo $! > bot.pid

echo "Бот запущен с PID: $(cat bot.pid)"
echo "Логи доступны в файле: logs/bot.log" 