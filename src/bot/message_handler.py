"""
Обработчик сообщений пользователей.

Отвечает только за бизнес-логику обработки пользовательских сообщений.
"""

import logging
from typing import Any

from .interfaces import DialogueStorage, LLMProvider, MediaProvider

logger = logging.getLogger(__name__)


class MessageHandler:
    """Обработчик пользовательских сообщений."""

    llm_provider: LLMProvider
    dialogue_storage: DialogueStorage
    media_provider: MediaProvider | None

    def __init__(
        self,
        llm_provider: LLMProvider,
        dialogue_storage: DialogueStorage,
        media_provider: MediaProvider | None = None,
    ) -> None:
        """
        Инициализация обработчика сообщений.

        Args:
            llm_provider: Провайдер LLM для генерации ответов
            dialogue_storage: Хранилище истории диалогов
            media_provider: Обработчик медиа-файлов (опционально для фото/аудио)
        """
        self.llm_provider = llm_provider
        self.dialogue_storage = dialogue_storage
        self.media_provider = media_provider
        logger.info("MessageHandler initialized")

    async def handle_user_message(self, user_id: int, username: str, text: str) -> str:
        """
        Обработать сообщение пользователя и получить ответ.

        Args:
            user_id: ID пользователя Telegram
            username: Имя пользователя Telegram
            text: Текст сообщения от пользователя

        Returns:
            Текст ответа от LLM

        Raises:
            Exception: Если произошла ошибка при обработке
        """
        logger.info(f"Processing message from user {user_id} (@{username}): {text[:50]}...")

        try:
            # Добавляем сообщение пользователя в историю
            await self.dialogue_storage.add_message(user_id, "user", text)

            # Получаем историю диалога
            history = await self.dialogue_storage.get_history(user_id)

            # Получаем ответ от LLM с учетом истории
            logger.info(f"Requesting LLM response for user {user_id}")
            response = self.llm_provider.get_response(history)

            # Добавляем ответ ассистента в историю
            await self.dialogue_storage.add_message(user_id, "assistant", response)

            logger.info(f"Generated response for user {user_id}: {response[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Error processing message from user {user_id}: {e}", exc_info=True)
            raise

    async def handle_photo_message(
        self,
        user_id: int,
        username: str,
        photo_file_id: str,
        caption: str | None,
        bot: Any,
    ) -> str:
        """
        Обработать фото от пользователя и получить ответ.

        Args:
            user_id: ID пользователя Telegram
            username: Имя пользователя Telegram
            photo_file_id: ID файла фото в Telegram
            caption: Подпись к фото (может быть None)
            bot: Экземпляр aiogram Bot для скачивания

        Returns:
            Текст ответа от LLM

        Raises:
            ValueError: Если MediaProvider не инициализирован
            Exception: Если произошла ошибка при обработке
        """
        if self.media_provider is None:
            raise ValueError("MediaProvider is required to handle photo messages")

        logger.info(
            f"Processing photo from user {user_id} (@{username}), "
            f"file_id: {photo_file_id}, caption: {caption}"
        )

        try:
            # Скачиваем фото
            photo_bytes = await self.media_provider.download_photo(photo_file_id, bot)

            # Конвертируем в base64
            base64_image = self.media_provider.photo_to_base64(photo_bytes)

            # Формируем мультимодальное сообщение
            text = caption if caption else "Проанализируй это изображение"
            multimodal_content: list[dict[str, Any]] = [
                {"type": "text", "text": text},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ]

            # Добавляем мультимодальное сообщение в историю
            await self.dialogue_storage.add_message(user_id, "user", multimodal_content)

            # Получаем историю диалога
            history = await self.dialogue_storage.get_history(user_id)

            # Получаем ответ от LLM с учетом истории
            logger.info(f"Requesting LLM response for photo from user {user_id}")
            response = self.llm_provider.get_response(history)

            # Добавляем ответ ассистента в историю
            await self.dialogue_storage.add_message(user_id, "assistant", response)

            logger.info(f"Generated response for photo from user {user_id}: {response[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Error processing photo from user {user_id}: {e}", exc_info=True)
            raise

    async def handle_voice_message(
        self,
        user_id: int,
        username: str,
        voice_file_id: str,
        bot: Any,
    ) -> str:
        """
        Обработать голосовое сообщение от пользователя.

        Args:
            user_id: ID пользователя Telegram
            username: Имя пользователя Telegram
            voice_file_id: ID файла голосового сообщения в Telegram
            bot: Экземпляр aiogram Bot для скачивания

        Returns:
            Текст ответа от LLM

        Raises:
            ValueError: Если MediaProvider не инициализирован
            Exception: Если произошла ошибка при обработке
        """
        if self.media_provider is None:
            raise ValueError("MediaProvider is required to handle voice messages")

        logger.info(f"Processing voice from user {user_id} (@{username}), file_id: {voice_file_id}")

        try:
            # Скачиваем аудио
            audio_bytes = await self.media_provider.download_audio(voice_file_id, bot)

            # Транскрибируем аудио в текст
            transcribed_text = await self.media_provider.transcribe_audio(audio_bytes)
            logger.info(f"Transcribed text from user {user_id}: {transcribed_text[:50]}...")

            # Обрабатываем как обычное текстовое сообщение
            return await self.handle_user_message(user_id, username, transcribed_text)

        except Exception as e:
            logger.error(f"Error processing voice from user {user_id}: {e}", exc_info=True)
            raise
