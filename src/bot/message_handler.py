"""
Обработчик сообщений пользователей.

Отвечает только за бизнес-логику обработки пользовательских сообщений.
"""

import logging

from .interfaces import DialogueStorage, LLMProvider

logger = logging.getLogger(__name__)


class MessageHandler:
    """Обработчик пользовательских сообщений."""

    llm_provider: LLMProvider
    dialogue_storage: DialogueStorage

    def __init__(self, llm_provider: LLMProvider, dialogue_storage: DialogueStorage) -> None:
        """
        Инициализация обработчика сообщений.

        Args:
            llm_provider: Провайдер LLM для генерации ответов
            dialogue_storage: Хранилище истории диалогов
        """
        self.llm_provider = llm_provider
        self.dialogue_storage = dialogue_storage
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
            self.dialogue_storage.add_message(user_id, "user", text)

            # Получаем историю диалога
            history = self.dialogue_storage.get_history(user_id)

            # Получаем ответ от LLM с учетом истории
            logger.info(f"Requesting LLM response for user {user_id}")
            response = self.llm_provider.get_response(history)

            # Добавляем ответ ассистента в историю
            self.dialogue_storage.add_message(user_id, "assistant", response)

            logger.info(f"Generated response for user {user_id}: {response[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Error processing message from user {user_id}: {e}", exc_info=True)
            raise
