"""
Интерфейсы (Protocols) для ключевых компонентов бота.

Используем Protocol вместо ABC для соблюдения Duck Typing и упрощения тестирования.
Это реализация Dependency Inversion Principle (SOLID).
"""

from typing import Protocol


class LLMProvider(Protocol):
    """
    Контракт для провайдеров LLM (Language Model).

    Любой класс, реализующий этот метод, может использоваться как LLM провайдер.
    """

    def get_response(self, messages: list[dict[str, str]]) -> str:
        """
        Получить ответ от LLM на основе истории сообщений.

        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}]

        Returns:
            Текст ответа от LLM

        Raises:
            Exception: Если произошла ошибка при обращении к LLM
        """
        ...


class DialogueStorage(Protocol):
    """
    Контракт для хранилищ диалогов.

    Любой класс, реализующий эти методы, может использоваться для хранения истории.
    """

    def add_message(self, user_id: int, role: str, content: str) -> None:
        """
        Добавить сообщение в историю диалога.

        Args:
            user_id: ID пользователя Telegram
            role: Роль отправителя ("user" или "assistant")
            content: Текст сообщения
        """
        ...

    def get_history(self, user_id: int) -> list[dict[str, str]]:
        """
        Получить историю диалога пользователя.

        Args:
            user_id: ID пользователя Telegram

        Returns:
            Список сообщений в формате [{"role": "user", "content": "..."}]
        """
        ...

    def clear_history(self, user_id: int) -> None:
        """
        Очистить историю диалога пользователя.

        Args:
            user_id: ID пользователя Telegram
        """
        ...
