"""
Обработчик команд Telegram бота.

Отвечает только за обработку команд (/start, /help, /reset).
"""

import logging

from .interfaces import DialogueStorage

logger = logging.getLogger(__name__)


class CommandHandler:
    """Обработчик команд бота."""

    dialogue_storage: DialogueStorage

    def __init__(self, dialogue_storage: DialogueStorage) -> None:
        """
        Инициализация обработчика команд.

        Args:
            dialogue_storage: Хранилище истории диалогов
        """
        self.dialogue_storage = dialogue_storage
        logger.info("CommandHandler initialized")

    def get_start_message(self) -> str:
        """
        Получить приветственное сообщение для команды /start.

        Returns:
            Текст приветственного сообщения
        """
        return (
            "👋 Привет! Я AI-ассистент на базе LLM.\n\n"
            "Я могу помочь тебе с различными вопросами, "
            "вести диалог и помнить контекст нашей беседы.\n\n"
            "📝 Доступные команды:\n"
            "/start - показать это сообщение\n"
            "/help - справка о командах\n"
            "/reset - очистить историю диалога\n\n"
            "Просто напиши мне свой вопрос!"
        )

    def get_help_message(self) -> str:
        """
        Получить справочное сообщение для команды /help.

        Returns:
            Текст справочного сообщения
        """
        return (
            "ℹ️ Справка по командам:\n\n"
            "/start - приветственное сообщение\n"
            "/help - это сообщение со справкой\n"
            "/reset - очистить историю нашего диалога\n\n"
            "💡 Как пользоваться:\n"
            "Просто отправь мне текстовое сообщение с вопросом, "
            "и я постараюсь на него ответить. Я помню контекст "
            "нашего диалога (до 20 последних сообщений)."
        )

    def reset_dialogue(self, user_id: int) -> str:
        """
        Очистить историю диалога пользователя.

        Args:
            user_id: ID пользователя Telegram

        Returns:
            Текст подтверждения очистки
        """
        self.dialogue_storage.clear_history(user_id)
        logger.info(f"Dialogue history cleared for user {user_id}")
        return "✅ История диалога очищена!\n\nТеперь можешь начать новый разговор."
