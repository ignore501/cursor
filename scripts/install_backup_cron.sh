#!/bin/bash

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo "Этот скрипт должен быть запущен с правами root"
    exit 1
fi

# Создание cron задачи для пользователя ronin
(crontab -u ronin -l 2>/dev/null; echo "0 0 * * * /home/ronin/ronin_tg_app/venv/bin/python /home/ronin/ronin_tg_app/scripts/backup_db.py --max-backups 3 >> /home/ronin/ronin_tg_app/logs/backup.log 2>> /home/ronin/ronin_tg_app/logs/backup.error.log") | crontab -u ronin -

echo "Cron задача установлена для пользователя ronin"
echo "Текущие cron задачи:"
crontab -u ronin -l 