"""
Обработчик медиа-файлов (фото, аудио).

Реализует MediaProvider Protocol для работы с изображениями и аудио.
"""

import base64
import logging
import tempfile
from pathlib import Path
from typing import Any, cast

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class MediaProcessor:
    """Обработчик медиа-файлов для Telegram бота."""

    def __init__(self, whisper_model: str = "base", whisper_device: str = "cpu") -> None:
        """
        Инициализация MediaProcessor с Faster-Whisper.

        Args:
            whisper_model: Модель Faster-Whisper ('tiny', 'base', 'small', 'medium', 'large')
            whisper_device: Устройство для выполнения ('cpu', 'cuda')
        """
        logger.info(f"Loading Faster-Whisper model: {whisper_model} on {whisper_device}")
        self.whisper = WhisperModel(whisper_model, device=whisper_device, compute_type="int8")
        logger.info("Faster-Whisper model loaded successfully")

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

    async def download_audio(self, file_id: str, bot: Any) -> bytes:
        """
        Скачать аудио из Telegram.

        Args:
            file_id: ID файла в Telegram (голосовое сообщение)
            bot: Экземпляр aiogram Bot

        Returns:
            Байты аудио файла (OGG format)

        Raises:
            Exception: Если произошла ошибка при скачивании
        """
        logger.info(f"Downloading audio with file_id: {file_id}")

        try:
            file = await bot.get_file(file_id)
            audio_io = await bot.download_file(file.file_path)
            audio_bytes = cast(bytes, audio_io.read())

            logger.info(f"Audio downloaded successfully: {len(audio_bytes)} bytes")
            return audio_bytes

        except Exception as e:
            logger.error(f"Error downloading audio {file_id}: {e}", exc_info=True)
            raise

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        """
        Транскрибировать аудио в текст через Faster-Whisper.

        Args:
            audio_bytes: Байты аудио файла (OGG format)

        Returns:
            Распознанный текст

        Raises:
            Exception: Если произошла ошибка при транскрибации
        """
        logger.info("Starting audio transcription with Faster-Whisper")

        try:
            # Сохранить аудио во временный файл (Faster-Whisper работает с файлами)
            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name

            try:
                # Транскрибация через Faster-Whisper
                segments, info = self.whisper.transcribe(temp_path, language="ru")
                text = " ".join([segment.text for segment in segments])

                logger.info(f"Transcription complete: {len(text)} chars, language: {info.language}")
                return text.strip()

            finally:
                # Удалить временный файл
                Path(temp_path).unlink(missing_ok=True)
                logger.debug(f"Temporary audio file deleted: {temp_path}")

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}", exc_info=True)
            raise
