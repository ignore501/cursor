#!/bin/bash

# Создаем директорию для логов если её нет
mkdir -p logs

# Проверяем статус бота
echo "Проверка статуса бота..."
python3 scripts/check_bot_status.py

# Если проверка прошла успешно, запускаем бота
if [ $? -eq 0 ]; then
    echo "Запуск бота..."
    
    # Останавливаем предыдущий процесс если он существует
    if [ -f bot.pid ]; then
        pid=$(cat bot.pid)
        if ps -p $pid > /dev/null; then
            echo "Останавливаем предыдущий процесс бота (PID: $pid)..."
            kill $pid
            sleep 2
        fi
    fi
    
    # Запускаем бота в фоновом режиме
    nohup python3 scripts/autopost.py > logs/bot.log 2>&1 &
    
    # Сохраняем PID
    echo $! > bot.pid
    
    echo "✅ Бот запущен с PID: $(cat bot.pid)"
    echo "📝 Логи доступны в файле: logs/bot.log"
else
    echo "❌ Запуск бота отменен из-за ошибок проверки"
    exit 1
fi 