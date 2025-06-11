"""
Модуль для управления голосованиями.
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class VoteManager:
    """Менеджер голосований."""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def get_current_topic(self) -> Optional[Dict]:
        """Получение текущей темы для голосования."""
        try:
            async with self.db_manager.get_connection() as db:
                db.row_factory = self.db_manager._get_row_factory()
                async with db.execute(
                    """
                    SELECT t.*, COUNT(v.vote_id) as total_votes
                    FROM topics t 
                    LEFT JOIN votes v ON t.id = v.topic_id 
                    WHERE t.status = 'active'
                    GROUP BY t.id 
                    ORDER BY t.created_at DESC 
                    LIMIT 1
                    """
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении текущей темы: {e}")
            return None

    async def create_vote(self, topic: str, title: str = "", description: str = "") -> Optional[int]:
        """Создание нового голосования."""
        if not topic:
            return None
        try:
            async with self.db_manager.get_connection() as db:
                cursor = await db.execute(
                    "INSERT INTO topics (topic, title, description, created_at) VALUES (?, ?, ?, ?)",
                    (topic, title, description, datetime.now(timezone.utc))
                )
                await db.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Ошибка при создании голосования: {e}")
            return None

    async def add_vote(self, user_id: int, topic_id: int, vote_type: str = "up") -> bool:
        """Добавление голоса за тему."""
        try:
            async with self.db_manager.get_connection() as db:
                # Проверяем, не голосовал ли уже пользователь
                async with db.execute(
                    "SELECT vote_id FROM votes WHERE user_id = ? AND topic_id = ?",
                    (user_id, topic_id)
                ) as cursor:
                    if await cursor.fetchone():
                        return False

                # Добавляем голос
                await db.execute(
                    "INSERT INTO votes (user_id, topic_id, vote_type) VALUES (?, ?, ?)",
                    (user_id, topic_id, vote_type)
                )
                
                # Обновляем счетчик голосов
                await db.execute(
                    "UPDATE topics SET votes = COALESCE(votes, 0) + 1 WHERE id = ?",
                    (topic_id,)
                )
                
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении голоса: {e}")
            return False

    async def get_top_topics(self, limit: int = 5) -> List[Dict]:
        """Получение топ тем для голосования."""
        try:
            async with self.db_manager.get_connection() as db:
                db.row_factory = self.db_manager._get_row_factory()
                async with db.execute(
                    """
                    SELECT t.*, COUNT(v.vote_id) as total_votes 
                    FROM topics t 
                    LEFT JOIN votes v ON t.id = v.topic_id 
                    GROUP BY t.id 
                    ORDER BY total_votes DESC 
                    LIMIT ?
                    """,
                    (limit,)
                ) as cursor:
                    return [dict(row) for row in await cursor.fetchall()]
        except Exception as e:
            logger.error(f"Ошибка при получении топ тем: {e}")
            return []

    async def get_vote_results(self, topic_id: int) -> Optional[Dict]:
        """Получение результатов голосования по теме."""
        try:
            async with self.db_manager.get_connection() as db:
                db.row_factory = self.db_manager._get_row_factory()
                async with db.execute(
                    """
                    SELECT t.*, COUNT(v.vote_id) as total_votes,
                           COUNT(CASE WHEN v.vote_type = 'up' THEN 1 END) as up_votes,
                           COUNT(CASE WHEN v.vote_type = 'down' THEN 1 END) as down_votes
                    FROM topics t 
                    LEFT JOIN votes v ON t.id = v.topic_id 
                    WHERE t.id = ?
                    GROUP BY t.id
                    """,
                    (topic_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении результатов голосования: {e}")
            return None

    async def get_user_votes(self, user_id: int) -> List[Dict]:
        """Получение голосов пользователя."""
        try:
            async with self.db_manager.get_connection() as db:
                db.row_factory = self.db_manager._get_row_factory()
                async with db.execute(
                    """
                    SELECT t.*, v.vote_type
                    FROM topics t 
                    JOIN votes v ON t.id = v.topic_id 
                    WHERE v.user_id = ?
                    ORDER BY v.created_at DESC
                    """,
                    (user_id,)
                ) as cursor:
                    return [dict(row) for row in await cursor.fetchall()]
        except Exception as e:
            logger.error(f"Ошибка при получении голосов пользователя: {e}")
            return [] 