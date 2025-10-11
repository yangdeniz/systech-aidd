"""
Интерфейсы (Protocols) для ключевых компонентов бота.

Используем Protocol вместо ABC для соблюдения Duck Typing и упрощения тестирования.
Это реализация Dependency Inversion Principle (SOLID).
"""

from typing import Any, Protocol


class LLMProvider(Protocol):
    """
    Контракт для провайдеров LLM (Language Model).

    Любой класс, реализующий этот метод, может использоваться как LLM провайдер.
    Поддерживает мультимодальные сообщения (текст + изображения).
    """

    def get_response(self, messages: list[dict[str, Any]]) -> str:
        """
        Получить ответ от LLM на основе истории сообщений.

        Args:
            messages: Список сообщений в формате:
                - Текстовое: [{"role": "user", "content": "..."}]
                - Мультимодальное: [{"role": "user", "content": [
                    {"type": "text", "text": "..."},
                    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
                  ]}]

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
    Поддерживает текстовые и мультимодальные сообщения (с изображениями).
    """

    def add_message(self, user_id: int, role: str, content: str | list[dict[str, Any]]) -> None:
        """
        Добавить сообщение в историю диалога.

        Args:
            user_id: ID пользователя Telegram
            role: Роль отправителя ("user" или "assistant")
            content: Текст сообщения или мультимодальный контент:
                - Текст: "Hello world"
                - Мультимодальный: [
                    {"type": "text", "text": "..."},
                    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
                  ]
        """
        ...

    def get_history(self, user_id: int) -> list[dict[str, Any]]:
        """
        Получить историю диалога пользователя.

        Args:
            user_id: ID пользователя Telegram

        Returns:
            Список сообщений в формате [{"role": "user", "content": "..." | [...]}]
        """
        ...

    def clear_history(self, user_id: int) -> None:
        """
        Очистить историю диалога пользователя.

        Args:
            user_id: ID пользователя Telegram
        """
        ...


class MediaProvider(Protocol):
    """
    Контракт для обработки медиа-файлов (фото, аудио).

    Любой класс, реализующий эти методы, может использоваться для работы с медиа.
    """

    async def download_photo(self, file_id: str, bot: Any) -> bytes:
        """
        Скачать фото из Telegram.

        Args:
            file_id: ID файла в Telegram
            bot: Экземпляр aiogram Bot для скачивания

        Returns:
            Байты изображения

        Raises:
            Exception: Если произошла ошибка при скачивании
        """
        ...

    def photo_to_base64(self, photo_bytes: bytes) -> str:
        """
        Конвертировать фото в base64 строку для передачи в Vision API.

        Args:
            photo_bytes: Байты изображения

        Returns:
            Base64 строка
        """
        ...
