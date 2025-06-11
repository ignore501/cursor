"""
Модуль для работы с базой данных.
"""
from datetime import datetime, timezone
import aiosqlite
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import os
import sqlite3
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class DatabaseManager:
    """Менеджер базы данных"""
    
    def __init__(self, db_path: str):
        """Инициализация менеджера базы данных"""
        self.db_path = db_path
        self._initialized = False
        self._connection: Optional[aiosqlite.Connection] = None
        self._ensure_db_directory()

    def _ensure_db_directory(self) -> None:
        """Создание директории для базы данных, если она не существует"""
        if db_dir := os.path.dirname(self.db_path):
            os.makedirs(db_dir, exist_ok=True)

    def _get_row_factory(self):
        """Получение фабрики строк для преобразования результатов запросов в словари"""
        return lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))

    @asynccontextmanager
    async def get_connection(self):
        """Получение соединения с базой данных"""
        try:
            if not self._connection:
                self._connection = await aiosqlite.connect(self.db_path)
                self._connection.row_factory = self._get_row_factory()
            yield self._connection
        except Exception as e:
            logger.error(f"Ошибка при подключении к базе данных: {e}")
            raise

    async def initialize(self) -> None:
        """Инициализация базы данных"""
        if self._initialized:
            return
        try:
            if db_dir := os.path.dirname(self.db_path):
                os.makedirs(db_dir, exist_ok=True)
            async with self.get_connection() as conn:
                # Создаем таблицы
                await self._create_tables(conn)
            self._initialized = True
            logger.info("База данных успешно инициализирована")
        except Exception as e:
            logger.error(f"Ошибка при инициализации базы данных: {e}")
            raise

    async def _create_tables(self, conn) -> None:
        """Создание таблиц в базе данных"""
        # Создаем таблицу пользователей
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Создаем таблицу сообщений
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Создаем таблицу соревнований
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS competitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competition_id TEXT UNIQUE,
                title TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Создаем таблицу тем
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                competition_id TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Создаем таблицу голосов
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER,
                user_id INTEGER,
                vote_type INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES topics(id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Создаем таблицу метрик обучения
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS learning_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                metric_name TEXT,
                value REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Создаем индексы для оптимизации запросов
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_votes_topic_id ON votes(topic_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_votes_user_id ON votes(user_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_competitions_status ON competitions(status)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_topics_competition_id ON topics(competition_id)')
        
        await conn.commit()

    async def save_message(self, conn, user_id: int, content: str) -> None:
        """Сохранение сообщения в базу данных"""
        await conn.execute(
            'INSERT INTO messages (user_id, content) VALUES (?, ?)',
            (user_id, content)
        )
        await conn.commit()

    async def get_user_messages(self, conn, user_id: int, limit: int = 10) -> List[Dict]:
        """Получение сообщений пользователя"""
        async with conn.execute(
            'SELECT * FROM messages WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def check_tables(self, conn) -> None:
        """Проверка наличия всех необходимых таблиц"""
        tables = ['users', 'messages', 'competitions', 'topics', 'votes', 'learning_metrics']
        for table in tables:
            async with conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)) as cursor:
                if not await cursor.fetchone():
                    raise RuntimeError(f"Таблица {table} не найдена")

    async def close(self):
        """Закрытие соединения с базой данных"""
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Получение пользователя по ID"""
        try:
            async with self.get_connection() as conn:
                async with conn.execute(
                    "SELECT * FROM users WHERE user_id = ?",
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя: {e}")
            return None

    async def add_user(self, user_id: int, username: str, first_name: str = "", last_name: str = "") -> bool:
        """Добавление пользователя"""
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    "INSERT OR REPLACE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
                    (user_id, username, first_name, last_name)
                )
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя: {e}")
            return False

    async def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """Получение статистики пользователя"""
        try:
            async with self.get_connection() as conn:
                # Получаем количество выполненных задач
                async with conn.execute(
                    "SELECT COUNT(*) as completed_tasks FROM learning_metrics WHERE user_id = ? AND metric_name = 'task_completed'",
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    completed_tasks = row['completed_tasks'] if row else 0

                # Получаем общее время обучения
                async with conn.execute(
                    "SELECT SUM(value) as total_time FROM learning_metrics WHERE user_id = ? AND metric_name = 'learning_time'",
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    total_time = row['total_time'] if row and row['total_time'] is not None else 0

                # Получаем количество достижений
                async with conn.execute(
                    "SELECT COUNT(*) as achievements FROM learning_metrics WHERE user_id = ? AND metric_name = 'achievement'",
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    achievements = row['achievements'] if row else 0

                return {
                    'completed_tasks': completed_tasks,
                    'progress': min(100, (completed_tasks / 10) * 100),  # Примерный расчет прогресса
                    'learning_time': f"{total_time}ч",
                    'achievements': achievements
                }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики пользователя: {e}")
            return None

    async def get_user_plan(self, user_id: int) -> Optional[Dict]:
        """Получение плана пользователя"""
        try:
            async with self.get_connection() as conn:
                async with conn.execute(
                                "SELECT * FROM learning_metrics WHERE user_id = ? AND metric_name IN ('goal', 'materials', 'time')",
                                (user_id,)
                            ) as cursor:
                    rows = await cursor.fetchall()
                    return {row['metric_name']: row['value'] for row in rows} if rows else None
        except Exception as e:
            logger.error(f"Ошибка при получении плана пользователя: {e}")
            return None

    async def add_message(self, user_id: int, text: str) -> Optional[int]:
        """Добавление сообщения"""
        try:
            async with self.get_connection() as db:
                cursor = await db.execute(
                    "INSERT INTO messages (user_id, text) VALUES (?, ?)",
                    (user_id, text)
                )
                await db.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Ошибка при добавлении сообщения: {e}")
            return None

    async def get_message(self, message_id: int) -> Optional[Dict[str, Any]]:
        """Получение сообщения"""
        try:
            async with self.get_connection() as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT * FROM messages WHERE message_id = ?",
                    (message_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении сообщения: {e}")
            return None

    async def add_topic(self, topic: str) -> Optional[int]:
        """Добавление темы"""
        try:
            async with self.get_connection() as db:
                cursor = await db.execute(
                    "INSERT INTO topics (topic, created_at) VALUES (?, ?)",
                    (topic, datetime.now(timezone.utc)),
                )
                await db.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Ошибка при добавлении темы: {e}")
            return None

    async def get_topic(self, topic_id: int) -> Optional[dict]:
        """Получение темы по ID"""
        try:
            async with self.get_connection() as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT * FROM topics WHERE id = ?",
                    (topic_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении темы: {str(e)}")
            return None

    async def get_topics(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Получение списка тем"""
        try:
            async with self.get_connection() as db:
                db.row_factory = aiosqlite.Row
                query = "SELECT * FROM topics ORDER BY created_at DESC"
                params = []
                
                if limit is not None:
                    query += " LIMIT ?"
                    params.append(limit)
                if offset is not None:
                    query += " OFFSET ?"
                    params.append(offset)
                
                async with db.execute(query, params) as cursor:
                    return [dict(row) for row in await cursor.fetchall()]
        except Exception as e:
            logger.error(f"Ошибка при получении тем: {e}")
            return []

    async def add_vote(self, user_id: int, topic_id: int, vote_type: str) -> bool:
        """Добавление голоса"""
        try:
            async with self.get_connection() as db:
                await db.execute(
                    "INSERT INTO votes (user_id, topic_id, vote_type) VALUES (?, ?, ?)",
                    (user_id, topic_id, vote_type)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении голоса: {e}")
            return False

    async def get_votes(self, topic_id: int) -> List[Dict[str, Any]]:
        """Получение голосов для темы"""
        try:
            async with self.get_connection() as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT * FROM votes WHERE topic_id = ?",
                    (topic_id,)
                ) as cursor:
                    return [dict(row) for row in await cursor.fetchall()]
        except Exception as e:
            logger.error(f"Ошибка при получении голосов: {e}")
            return []

    async def is_user_blocked(self, user_id: int) -> bool:
        """Проверка блокировки пользователя"""
        try:
            async with self.get_connection() as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT is_blocked FROM users WHERE user_id = ?",
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Ошибка при проверке блокировки пользователя: {e}")
            return False

    async def block_user(self, user_id: int) -> bool:
        """Блокировка пользователя"""
        try:
            async with self.get_connection() as db:
                await db.execute(
                    "UPDATE users SET is_blocked = TRUE WHERE user_id = ?",
                    (user_id,)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при блокировке пользователя: {e}")
            return False

    async def unblock_user(self, user_id: int) -> bool:
        """Разблокировка пользователя"""
        try:
            async with self.get_connection() as db:
                await db.execute(
                    "UPDATE users SET is_blocked = FALSE WHERE user_id = ?",
                    (user_id,)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при разблокировке пользователя: {e}")
            return False

    async def get_user_topics(self, user_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Получение тем пользователя"""
        try:
            async with self.get_connection() as db:
                db.row_factory = aiosqlite.Row
                query = "SELECT * FROM topics WHERE user_id = ? ORDER BY created_at DESC"
                params = [user_id]
                
                if limit is not None:
                    query += " LIMIT ?"
                    params.append(limit)
                
                async with db.execute(query, params) as cursor:
                    return [dict(row) for row in await cursor.fetchall()]
        except Exception as e:
            logger.error(f"Ошибка при получении тем пользователя: {e}")
            return [] 