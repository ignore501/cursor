"""
Модуль для работы с базой данных SQLite.
"""
import asyncio
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from contextlib import asynccontextmanager

from config import BASE_DIR

class Database:
    """Класс для работы с базой данных."""

    def __init__(self, db_path: Path = BASE_DIR / "data" / "bot.db"):
        """Инициализация базы данных."""
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._pool = asyncio.Queue(maxsize=10)  # Пул соединений
        self._init_pool()
        self._init_db()

    def _init_pool(self) -> None:
        """Инициализация пула соединений."""
        for _ in range(10):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            self._pool.put_nowait(conn)

    @asynccontextmanager
    async def _get_connection(self):
        """Получение соединения из пула."""
        conn = await self._pool.get()
        try:
            yield conn
        finally:
            await self._pool.put(conn)

    def _init_db(self) -> None:
        """Инициализация таблиц базы данных."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    warnings INTEGER DEFAULT 0,
                    is_blocked BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица сообщений
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Таблица тем для голосования
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS voting_topics (
                    topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    proposed_by INTEGER,
                    votes INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (proposed_by) REFERENCES users (user_id)
                )
            """)
            
            # Индексы для оптимизации запросов
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_voting_topics_votes ON voting_topics(votes)")
            
            conn.commit()

    async def add_user(self, user_id: int, username: str, first_name: str, last_name: str) -> None:
        """Добавление нового пользователя."""
        async with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, first_name, last_name))
            conn.commit()

    async def add_message(self, user_id: int, text: str) -> None:
        """Добавление нового сообщения."""
        async with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (user_id, text)
                VALUES (?, ?)
            """, (user_id, text))
            conn.commit()

    async def add_warning(self, user_id: int) -> int:
        """Добавление предупреждения пользователю."""
        async with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET warnings = warnings + 1
                WHERE user_id = ?
            """, (user_id,))
            cursor.execute("""
                SELECT warnings FROM users WHERE user_id = ?
            """, (user_id,))
            warnings = cursor.fetchone()[0]
            conn.commit()
            return warnings

    async def block_user(self, user_id: int) -> None:
        """Блокировка пользователя."""
        async with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET is_blocked = 1
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()

    async def unblock_user(self, user_id: int) -> None:
        """Разблокировка пользователя."""
        async with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET is_blocked = 0, warnings = 0
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()

    async def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """Получение статистики пользователя."""
        async with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.*, COUNT(m.message_id) as message_count
                FROM users u
                LEFT JOIN messages m ON u.user_id = m.user_id
                WHERE u.user_id = ?
                GROUP BY u.user_id
            """, (user_id,))
            result = cursor.fetchone()
            
            if result:
                return dict(result)
            return None

    async def get_message_count(self, user_id: Optional[int], time_delta: timedelta) -> int:
        """Получение количества сообщений за период."""
        async with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if user_id is None:
                cursor.execute("""
                    SELECT COUNT(*) FROM messages
                    WHERE created_at >= datetime('now', ?)
                """, (f"-{time_delta.total_seconds()} seconds",))
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM messages
                    WHERE user_id = ? AND created_at >= datetime('now', ?)
                """, (user_id, f"-{time_delta.total_seconds()} seconds"))
                
            return cursor.fetchone()[0]

    async def get_messages_per_period(self, user_id: int) -> Dict[str, int]:
        """Получение количества сообщений за разные периоды."""
        tasks = [
            self.get_message_count(user_id, timedelta(minutes=1)),
            self.get_message_count(user_id, timedelta(hours=1)),
            self.get_message_count(user_id, timedelta(days=1))
        ]
        results = await asyncio.gather(*tasks)
        return {
            "per_minute": results[0],
            "per_hour": results[1],
            "per_day": results[2]
        }

    async def add_voting_topic(self, topic: str, proposed_by: int) -> int:
        """Добавление новой темы для голосования."""
        async with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO voting_topics (topic, proposed_by)
                VALUES (?, ?)
            """, (topic, proposed_by))
            topic_id = cursor.lastrowid
            conn.commit()
            return topic_id

    async def get_voting_topics(self, limit: int = 10) -> List[Tuple]:
        """Получение списка тем для голосования."""
        async with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT topic_id, topic, votes, created_at
                FROM voting_topics
                ORDER BY votes DESC, created_at DESC
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()

    async def vote_for_topic(self, topic_id: int) -> None:
        """Голосование за тему."""
        async with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE voting_topics
                SET votes = votes + 1
                WHERE topic_id = ?
            """, (topic_id,))
            conn.commit() 