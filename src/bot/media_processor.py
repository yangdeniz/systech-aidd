"""
Обработчик медиа-файлов (фото, аудио).

Реализует MediaProvider Protocol для работы с изображениями и аудио.
"""

import base64
import logging
from typing import Any, cast

logger = logging.getLogger(__name__)


class MediaProcessor:
    """Обработчик медиа-файлов для Telegram бота."""

    async def download_photo(self, file_id: str, bot: Any) -> bytes:
        """
        Скачать фото из Telegram.

        Args:
            file_id: ID файла в Telegram
            bot: Экземпляр aiogram Bot

        Returns:
            Байты изображения

        Raises:
            Exception: Если произошла ошибка при скачивании
        """
        logger.info(f"Downloading photo with file_id: {file_id}")

        try:
            file = await bot.get_file(file_id)
            photo_io = await bot.download_file(file.file_path)
            photo_bytes = cast(bytes, photo_io.read())

            logger.info(f"Photo downloaded successfully: {len(photo_bytes)} bytes")
            return photo_bytes

        except Exception as e:
            logger.error(f"Error downloading photo {file_id}: {e}", exc_info=True)
            raise

    def photo_to_base64(self, photo_bytes: bytes) -> str:
        """
        Конвертировать фото в base64 строку.

        Args:
            photo_bytes: Байты изображения

        Returns:
            Base64 строка
        """
        logger.debug(f"Converting photo to base64: {len(photo_bytes)} bytes")
        base64_str = base64.b64encode(photo_bytes).decode("utf-8")
        logger.debug(f"Base64 conversion complete: {len(base64_str)} chars")
        return base64_str
