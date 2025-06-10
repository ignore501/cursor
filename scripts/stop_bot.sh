#!/bin/bash

if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "Бот остановлен (PID: $PID)"
    else
        echo "Бот не запущен"
    fi
    rm bot.pid
else
    echo "Файл bot.pid не найден"
fi 