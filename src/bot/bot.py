import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .command_handler import CommandHandler
from .message_handler import MessageHandler
from .repository import UserRepository

logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Telegram бот - отвечает только за инфраструктуру aiogram.

    Делегирует обработку команд в CommandHandler,
    обработку сообщений в MessageHandler.
    Автоматически отслеживает пользователей через UserRepository.
    """

    bot: Bot
    dp: Dispatcher
    message_handler: MessageHandler
    command_handler: CommandHandler
    session_factory: async_sessionmaker[AsyncSession]

    def __init__(
        self,
        token: str,
        message_handler: MessageHandler,
        command_handler: CommandHandler,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """
        Инициализация Telegram бота.

        Args:
            token: Токен Telegram бота
            message_handler: Обработчик пользовательских сообщений
            command_handler: Обработчик команд бота
            session_factory: Фабрика сессий для создания UserRepository
        """
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.message_handler = message_handler
        self.command_handler = command_handler
        self.session_factory = session_factory
        self._register_handlers()
        logger.info("TelegramBot instance created")

    def _register_handlers(self) -> None:
        self.dp.message(Command("start"))(self.cmd_start)
        self.dp.message(Command("role"))(self.cmd_role)
        self.dp.message(Command("help"))(self.cmd_help)
        self.dp.message(Command("reset"))(self.cmd_reset)
        # Обработчики медиа должны быть ДО текстовых сообщений
        self.dp.message(lambda m: m.photo is not None)(self.handle_photo)
        self.dp.message(lambda m: m.voice is not None)(self.handle_voice)
        self.dp.message()(self.handle_message)

    async def _track_user(self, message: Message) -> int | None:
        """
        Отследить пользователя в базе данных.

        Создает или обновляет запись пользователя, обновляет last_seen.

        Args:
            message: Telegram сообщение с информацией о пользователе

        Returns:
            Внутренний user.id из базы данных или None, если пользователь не найден
        """
        if message.from_user is None:
            return None

        async with self.session_factory() as session:
            user_repo = UserRepository(session)
            user = await user_repo.get_or_create_user(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code,
            )
            return user.id

    async def cmd_start(self, message: Message) -> None:
        """Обработать команду /start."""
        if message.from_user is None:
            return

        # Отслеживаем пользователя
        await self._track_user(message)

        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        logger.info(f"User {user_id} (@{username}) executed /start command")

        response = self.command_handler.get_start_message()
        await message.answer(response)

    async def cmd_role(self, message: Message) -> None:
        """Обработать команду /role."""
        if message.from_user is None:
            return

        # Отслеживаем пользователя
        await self._track_user(message)

        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        logger.info(f"User {user_id} (@{username}) executed /role command")

        response = self.command_handler.get_role_message()
        await message.answer(response)

    async def cmd_help(self, message: Message) -> None:
        """Обработать команду /help."""
        if message.from_user is None:
            return

        # Отслеживаем пользователя
        await self._track_user(message)

        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        logger.info(f"User {user_id} (@{username}) executed /help command")

        response = self.command_handler.get_help_message()
        await message.answer(response)

    async def cmd_reset(self, message: Message) -> None:
        """Обработать команду /reset."""
        if message.from_user is None:
            return

        # Отслеживаем пользователя и получаем внутренний user.id
        user_id = await self._track_user(message)
        if user_id is None:
            return

        telegram_id = message.from_user.id
        username = message.from_user.username or "unknown"
        logger.info(f"User {telegram_id} (@{username}) executed /reset command")

        response = await self.command_handler.reset_dialogue(user_id)
        await message.answer(response)

    async def handle_message(self, message: Message) -> None:
        """Обработать пользовательское сообщение."""
        if message.from_user is None or message.text is None:
            return

        # Отслеживаем пользователя и получаем внутренний user.id
        user_id = await self._track_user(message)
        if user_id is None:
            return

        telegram_id = message.from_user.id
        username = message.from_user.username or "unknown"

        try:
            # Делегируем обработку в MessageHandler
            response = await self.message_handler.handle_user_message(
                user_id, username, message.text
            )
            await message.answer(response)

        except Exception as e:
            logger.error(f"Error handling message from user {telegram_id}: {e}", exc_info=True)
            await message.answer(
                "Извините, произошла ошибка при обработке вашего сообщения. "
                "Попробуйте еще раз или используйте /reset для очистки истории."
            )

    async def handle_photo(self, message: Message) -> None:
        """Обработать фото от пользователя."""
        if message.from_user is None or message.photo is None:
            return

        # Отслеживаем пользователя и получаем внутренний user.id
        user_id = await self._track_user(message)
        if user_id is None:
            return

        telegram_id = message.from_user.id
        username = message.from_user.username or "unknown"

        # Получаем последнее фото (самого большого размера)
        photo = message.photo[-1]
        photo_file_id = photo.file_id
        caption = message.caption

        logger.info(
            f"User {telegram_id} (@{username}) sent photo: file_id={photo_file_id}, caption={caption}"
        )

        try:
            # Делегируем обработку в MessageHandler
            response = await self.message_handler.handle_photo_message(
                user_id, username, photo_file_id, caption, self.bot
            )
            await message.answer(response)

        except Exception as e:
            logger.error(f"Error handling photo from user {telegram_id}: {e}", exc_info=True)
            await message.answer(
                "Извините, произошла ошибка при обработке вашего изображения. "
                "Попробуйте еще раз или используйте /reset для очистки истории."
            )

    async def handle_voice(self, message: Message) -> None:
        """Обработать голосовое сообщение от пользователя."""
        if message.from_user is None or message.voice is None:
            return

        # Отслеживаем пользователя и получаем внутренний user.id
        user_id = await self._track_user(message)
        if user_id is None:
            return

        telegram_id = message.from_user.id
        username = message.from_user.username or "unknown"

        voice_file_id = message.voice.file_id

        logger.info(f"User {telegram_id} (@{username}) sent voice: file_id={voice_file_id}")

        try:
            # Делегируем обработку в MessageHandler
            response = await self.message_handler.handle_voice_message(
                user_id, username, voice_file_id, self.bot
            )
            await message.answer(response)

        except Exception as e:
            logger.error(f"Error handling voice from user {telegram_id}: {e}", exc_info=True)
            await message.answer(
                "Извините, произошла ошибка при обработке вашего голосового сообщения. "
                "Попробуйте еще раз или используйте /reset для очистки истории."
            )

    async def start(self) -> None:
        await self.dp.start_polling(self.bot)
