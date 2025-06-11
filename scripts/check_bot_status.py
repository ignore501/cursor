#!/usr/bin/env python3
"""
Скрипт для проверки статуса бота и его прав.
"""
import os
import sys
import logging
import asyncio
from telegram import Bot
from telegram.error import TelegramError, Forbidden
from src.config.config import get_config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot_status.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def check_bot_status():
    """Проверка статуса бота и его прав."""
    try:
        # Получаем конфигурацию
        config = get_config()
        
        # Проверяем наличие необходимых переменных
        if not config.TELEGRAM_BOT_TOKEN:
            logger.error("❌ Токен бота не найден в конфигурации")
            sys.exit(1)
            
        if not config.TELEGRAM_CHANNEL_ID:
            logger.error("❌ ID канала не найден в конфигурации")
            sys.exit(1)
        
        # Создаем экземпляр бота
        bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        
        # Проверяем подключение к API
        logger.info("Проверка подключения к Telegram API...")
        await bot.get_me()
        logger.info("✅ Подключение к Telegram API успешно")
        
        # Проверяем права в канале
        logger.info(f"Проверка прав в канале {config.TELEGRAM_CHANNEL_ID}...")
        try:
            # Пробуем получить информацию о канале
            chat = await bot.get_chat(config.TELEGRAM_CHANNEL_ID)
            logger.info(f"✅ Канал найден: {chat.title}")
            
            # Проверяем права бота
            bot_member = await bot.get_chat_member(
                chat_id=config.TELEGRAM_CHANNEL_ID,
                user_id=(await bot.get_me()).id
            )
            
            # Проверяем необходимые права
            required_permissions = {
                "can_post_messages": "Отправка сообщений",
                "can_edit_messages": "Редактирование сообщений",
                "can_delete_messages": "Удаление сообщений"
            }
            
            for permission, description in required_permissions.items():
                if getattr(bot_member, permission, False):
                    logger.info(f"✅ {description}: Разрешено")
                else:
                    logger.warning(f"⚠️ {description}: Запрещено")
            
            # Проверяем процесс бота
            if os.path.exists('bot.pid'):
                with open('bot.pid', 'r') as f:
                    pid = f.read().strip()
                if os.path.exists(f'/proc/{pid}'):
                    logger.info(f"✅ Бот запущен (PID: {pid})")
                else:
                    logger.warning("⚠️ Бот не запущен")
            else:
                logger.warning("⚠️ Файл PID не найден")
            
            # Проверяем логи
            if os.path.exists('logs/bot.log'):
                logger.info("✅ Файл логов существует")
            else:
                logger.warning("⚠️ Файл логов не найден")
            
        except TelegramError as e:
            logger.error(f"❌ Ошибка при проверке канала: {e}")
            sys.exit(1)
            
    except Forbidden:
        logger.error("❌ Неверный токен бота")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Создаем директорию для логов если её нет
    os.makedirs('logs', exist_ok=True)
    
    # Запускаем проверку
    asyncio.run(check_bot_status()) 