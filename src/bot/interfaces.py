"""
Интерфейсы (Protocols) для ключевых компонентов бота.

Используем Protocol вместо ABC для соблюдения Duck Typing и упрощения тестирования.
Это реализация Dependency Inversion Principle (SOLID).
"""

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from .models import User


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

    Все методы асинхронные для поддержки персистентного хранения в БД.
    """

    async def add_message(
        self, user_id: int, role: str, content: str | list[dict[str, Any]]
    ) -> None:
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

    async def get_history(self, user_id: int) -> list[dict[str, Any]]:
        """
        Получить историю диалога пользователя.

        Args:
            user_id: ID пользователя Telegram

        Returns:
            Список сообщений в формате [{"role": "user", "content": "..." | [...]}]
        """
        ...

    async def clear_history(self, user_id: int) -> None:
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

    async def download_audio(self, file_id: str, bot: Any) -> bytes:
        """
        Скачать аудио из Telegram.

        Args:
            file_id: ID файла в Telegram (голосовое сообщение)
            bot: Экземпляр aiogram Bot для скачивания

        Returns:
            Байты аудио файла (OGG format)

        Raises:
            Exception: Если произошла ошибка при скачивании
        """
        ...

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
        ...


class UserStorage(Protocol):
    """
    Контракт для хранилищ пользователей.

    Любой класс, реализующий эти методы, может использоваться для работы с пользователями.
    Все методы асинхронные для поддержки персистентного хранения в БД.
    """

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        language_code: str | None = None,
    ) -> "User":
        """
        Получить пользователя или создать нового.

        Автоматически обновляет last_seen и данные пользователя при каждом вызове.

        Args:
            telegram_id: ID пользователя Telegram
            username: Username из Telegram (может быть None)
            first_name: Имя пользователя (может быть None)
            last_name: Фамилия пользователя (может быть None)
            language_code: Код языка (может быть None)

        Returns:
            Объект User (существующий или новый)
        """
        ...

    async def update_last_seen(self, telegram_id: int) -> None:
        """
        Обновить время последнего взаимодействия пользователя.

        Args:
            telegram_id: ID пользователя Telegram
        """
        ...
