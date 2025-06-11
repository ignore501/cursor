#!/bin/bash

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo "Этот скрипт должен быть запущен с правами root"
    exit 1
fi

# Пути
SERVICE_FILE="db_backup.service"
SERVICE_PATH="/etc/systemd/system/db_backup.service"
APP_DIR="/home/ronin/ronin_tg_app"

# Проверка существования директории приложения
if [ ! -d "$APP_DIR" ]; then
    echo "Директория приложения не найдена: $APP_DIR"
    exit 1
fi

# Копирование файла сервиса
cp "$SERVICE_FILE" "$SERVICE_PATH"

# Установка прав
chmod 644 "$SERVICE_PATH"

# Перезагрузка systemd
systemctl daemon-reload

# Включение и запуск сервиса
systemctl enable db_backup.service
systemctl start db_backup.service

echo "Сервис бэкапа установлен и запущен"
echo "Статус:"
systemctl status db_backup.service 