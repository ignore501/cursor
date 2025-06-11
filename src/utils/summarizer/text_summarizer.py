import logging
from typing import Optional
from transformers import pipeline

logger = logging.getLogger(__name__)

class TextSummarizer:
    def __init__(self):
        try:
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        except Exception as e:
            logger.error(f"Ошибка при инициализации суммаризатора: {e}")
            self.summarizer = None

    async def summarize_text(self, text: str, max_length: int = 130, min_length: int = 30) -> Optional[str]:
        """Суммаризация текста"""
        if not self.summarizer:
            logger.error("Суммаризатор не инициализирован")
            return None

        try:
            # Разбиваем текст на части, если он слишком длинный
            chunks = self._split_text(text)
            summaries = []

            for chunk in chunks:
                summary = self.summarizer(
                    chunk,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                summaries.append(summary[0]['summary_text'])

            return " ".join(summaries)
        except Exception as e:
            logger.error(f"Ошибка при суммаризации текста: {e}")
            return None

    def _split_text(self, text: str, max_length: int = 1024) -> list:
        """Разбиение текста на части"""
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            if len(" ".join(current_chunk)) > max_length:
                chunks.append(" ".join(current_chunk[:-1]))
                current_chunk = [word]

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks 