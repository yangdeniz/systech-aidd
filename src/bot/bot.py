import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from llm_client import LLMClient
from dialogue_manager import DialogueManager

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token: str, llm_client: LLMClient, dialogue_manager: DialogueManager):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.llm_client = llm_client
        self.dialogue_manager = dialogue_manager
        self._register_handlers()
        logger.info("TelegramBot instance created")

    def _register_handlers(self):
        self.dp.message(Command("start"))(self.cmd_start)
        self.dp.message(Command("help"))(self.cmd_help)
        self.dp.message(Command("reset"))(self.cmd_reset)
        self.dp.message()(self.handle_message)

    async def cmd_start(self, message: Message):
        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        logger.info(f"User {user_id} (@{username}) executed /start command")
        
        await message.answer(
            "👋 Привет! Я AI-ассистент на базе LLM.\n\n"
            "Я могу помочь тебе с различными вопросами, "
            "вести диалог и помнить контекст нашей беседы.\n\n"
            "📝 Доступные команды:\n"
            "/start - показать это сообщение\n"
            "/help - справка о командах\n"
            "/reset - очистить историю диалога\n\n"
            "Просто напиши мне свой вопрос!"
        )

    async def cmd_help(self, message: Message):
        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        logger.info(f"User {user_id} (@{username}) executed /help command")
        
        await message.answer(
            "ℹ️ Справка по командам:\n\n"
            "/start - приветственное сообщение\n"
            "/help - это сообщение со справкой\n"
            "/reset - очистить историю нашего диалога\n\n"
            "💡 Как пользоваться:\n"
            "Просто отправь мне текстовое сообщение с вопросом, "
            "и я постараюсь на него ответить. Я помню контекст "
            "нашего диалога (до 20 последних сообщений)."
        )

    async def cmd_reset(self, message: Message):
        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        logger.info(f"User {user_id} (@{username}) executed /reset command")
        
        self.dialogue_manager.clear_history(user_id)
        
        await message.answer(
            "✅ История диалога очищена!\n\n"
            "Теперь можешь начать новый разговор."
        )
    
    async def handle_message(self, message: Message):
        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        
        logger.info(f"Received message from user {user_id} (@{username}): {message.text[:50]}...")
        
        try:
            # Добавляем сообщение пользователя в историю
            self.dialogue_manager.add_message(user_id, "user", message.text)
            
            # Получаем историю диалога
            history = self.dialogue_manager.get_history(user_id)
            
            # Получаем ответ от LLM с учетом истории
            logger.info(f"Requesting LLM response for user {user_id}")
            response = self.llm_client.get_response(history)
            
            # Добавляем ответ ассистента в историю
            self.dialogue_manager.add_message(user_id, "assistant", response)
            
            # Отправляем ответ пользователю
            await message.answer(response)
            logger.info(f"Sent response to user {user_id}: {response[:50]}...")
            
        except Exception as e:
            logger.error(f"Error handling message from user {user_id}: {e}", exc_info=True)
            await message.answer(
                "Извините, произошла ошибка при обработке вашего сообщения. "
                "Попробуйте еще раз или используйте /reset для очистки истории."
            )
    
    async def start(self):
        await self.dp.start_polling(self.bot)

