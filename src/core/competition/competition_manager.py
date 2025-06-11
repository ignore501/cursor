"""
Модуль для управления контекстом соревнований.
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from src.utils.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class CompetitionManager:
    """Менеджер соревнований."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._current_competition: Optional[Dict[str, Any]] = None

    async def set_current_competition(self, competition_id: str) -> bool:
        """Установка текущего соревнования."""
        try:
            async with self.db_manager.get_connection() as db:
                # Проверяем существование соревнования
                async with db.execute(
                    "SELECT * FROM competitions WHERE competition_id = ?",
                    (competition_id,)
                ) as cursor:
                    competition = await cursor.fetchone()
                    
                    if not competition:
                        # Если соревнование не существует, создаем его
                        await db.execute(
                            """
                            INSERT INTO competitions 
                            (competition_id, title, description, created_at, status)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (competition_id, f"Competition {competition_id}", 
                             "Auto-created competition", datetime.now(), "active")
                        )
                        await db.commit()
                        
                        # Получаем созданное соревнование
                        async with db.execute(
                            "SELECT * FROM competitions WHERE competition_id = ?",
                            (competition_id,)
                        ) as cursor:
                            competition = await cursor.fetchone()
                    
                    self._current_competition = dict(competition)
                    return True
                    
        except Exception as e:
            logger.error(f"Ошибка при установке текущего соревнования: {e}")
            return False

    async def get_current_competition(self) -> Optional[Dict[str, Any]]:
        """Получение информации о текущем соревновании."""
        if not self._current_competition:
            try:
                async with self.db_manager.get_connection() as db:
                    async with db.execute(
                        "SELECT * FROM competitions WHERE status = 'active' ORDER BY created_at DESC LIMIT 1"
                    ) as cursor:
                        competition = await cursor.fetchone()
                        if competition:
                            self._current_competition = dict(competition)
            except Exception as e:
                logger.error(f"Ошибка при получении текущего соревнования: {e}")
        return self._current_competition

    async def get_competition_id(self) -> Optional[str]:
        """Получение ID текущего соревнования."""
        competition = await self.get_current_competition()
        return competition.get('competition_id') if competition else None

    async def list_competitions(self) -> list[Dict[str, Any]]:
        """Получение списка всех соревнований."""
        try:
            async with self.db_manager.get_connection() as db:
                async with db.execute(
                    "SELECT * FROM competitions ORDER BY created_at DESC"
                ) as cursor:
                    return [dict(row) for row in await cursor.fetchall()]
        except Exception as e:
            logger.error(f"Ошибка при получении списка соревнований: {e}")
            return [] 