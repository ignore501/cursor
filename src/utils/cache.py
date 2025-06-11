"""
Модуль для работы с Redis кешем.
"""
import json
from typing import Any, Optional
import aioredis
from functools import wraps
import structlog

from src.config.config import REDIS_URL
from src.utils.metrics import Metrics, track_time

logger = structlog.get_logger()

class Cache:
    """Класс для работы с Redis кешем."""
    
    def __init__(self):
        """Инициализация Redis соединения."""
        self.redis = None
        
    async def init(self) -> None:
        """Инициализация пула соединений Redis."""
        self.redis = await aioredis.create_redis_pool(REDIS_URL)
        logger.info("redis_connected", url=REDIS_URL)
        
    async def close(self) -> None:
        """Закрытие соединения с Redis."""
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()
            logger.info("redis_disconnected")
            
    @track_time(Metrics.db_latency)
    async def get(self, key: str) -> Optional[Any]:
        """Получение значения из кеша."""
        if not self.redis:
            return None
            
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.error("cache_decode_error", key=key)
                return None
        return None
        
    @track_time(Metrics.db_latency)
    async def set(self, key: str, value: Any, expire: int = 3600) -> None:
        """Сохранение значения в кеш."""
        if not self.redis:
            return
            
        try:
            await self.redis.set(
                key,
                json.dumps(value),
                expire=expire
            )
        except Exception as e:
            logger.error("cache_set_error", 
                        key=key,
                        error=str(e))
            
    @track_time(Metrics.db_latency)
    async def delete(self, key: str) -> None:
        """Удаление значения из кеша."""
        if not self.redis:
            return
            
        await self.redis.delete(key)
        
    @track_time(Metrics.db_latency)
    async def clear(self) -> None:
        """Очистка всего кеша."""
        if not self.redis:
            return
            
        await self.redis.flushdb()
        logger.info("cache_cleared")

# Синглтон для кеша
cache = Cache()

def cached(expire: int = 3600):
    """Декоратор для кеширования результатов функций."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Генерация ключа кеша
            key = f"{func.__name__}:{args}:{kwargs}"
            
            # Попытка получить из кеша
            cached_value = await cache.get(key)
            if cached_value is not None:
                return cached_value
                
            # Выполнение функции
            result = await func(*args, **kwargs)
            
            # Сохранение в кеш
            await cache.set(key, result, expire)
            
            return result
        return wrapper
    return decorator 