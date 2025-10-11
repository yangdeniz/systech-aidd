import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from .command_handler import CommandHandler
from .message_handler import MessageHandler

logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Telegram бот - отвечает только за инфраструктуру aiogram.

    Делегирует обработку команд в CommandHandler,
    обработку сообщений в MessageHandler.
    """

    bot: Bot
    dp: Dispatcher
    message_handler: MessageHandler
    command_handler: CommandHandler

    def __init__(
        self, token: str, message_handler: MessageHandler, command_handler: CommandHandler
    ) -> None:
        """
        Инициализация Telegram бота.

        Args:
            token: Токен Telegram бота
            message_handler: Обработчик пользовательских сообщений
            command_handler: Обработчик команд бота
        """
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.message_handler = message_handler
        self.command_handler = command_handler
        self._register_handlers()
        logger.info("TelegramBot instance created")

    def _register_handlers(self) -> None:
        self.dp.message(Command("start"))(self.cmd_start)
        self.dp.message(Command("help"))(self.cmd_help)
        self.dp.message(Command("reset"))(self.cmd_reset)
        self.dp.message()(self.handle_message)

    async def cmd_start(self, message: Message) -> None:
        """Обработать команду /start."""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        logger.info(f"User {user_id} (@{username}) executed /start command")

        response = self.command_handler.get_start_message()
        await message.answer(response)

    async def cmd_help(self, message: Message) -> None:
        """Обработать команду /help."""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        logger.info(f"User {user_id} (@{username}) executed /help command")

        response = self.command_handler.get_help_message()
        await message.answer(response)

    async def cmd_reset(self, message: Message) -> None:
        """Обработать команду /reset."""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        logger.info(f"User {user_id} (@{username}) executed /reset command")

        response = self.command_handler.reset_dialogue(user_id)
        await message.answer(response)

    async def handle_message(self, message: Message) -> None:
        """Обработать пользовательское сообщение."""
        if message.from_user is None or message.text is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "unknown"

        try:
            # Делегируем обработку в MessageHandler
            response = await self.message_handler.handle_user_message(
                user_id, username, message.text
            )
            await message.answer(response)

        except Exception as e:
            logger.error(f"Error handling message from user {user_id}: {e}", exc_info=True)
            await message.answer(
                "Извините, произошла ошибка при обработке вашего сообщения. "
                "Попробуйте еще раз или используйте /reset для очистки истории."
            )

    async def start(self) -> None:
        await self.dp.start_polling(self.bot)
