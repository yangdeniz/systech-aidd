from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from llm_client import LLMClient
from dialogue_manager import DialogueManager


class TelegramBot:
    def __init__(self, token: str, llm_client: LLMClient, dialogue_manager: DialogueManager):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.llm_client = llm_client
        self.dialogue_manager = dialogue_manager
        self._register_handlers()

    def _register_handlers(self):
        self.dp.message(Command("start"))(self.cmd_start)
        self.dp.message(Command("help"))(self.cmd_help)
        self.dp.message(Command("reset"))(self.cmd_reset)
        self.dp.message()(self.handle_message)

    async def cmd_start(self, message: Message):
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
        self.dialogue_manager.clear_history(user_id)
        await message.answer(
            "✅ История диалога очищена!\n\n"
            "Теперь можешь начать новый разговор."
        )
    
    async def handle_message(self, message: Message):
        user_id = message.from_user.id
        
        # Добавляем сообщение пользователя в историю
        self.dialogue_manager.add_message(user_id, "user", message.text)
        
        # Получаем историю диалога
        history = self.dialogue_manager.get_history(user_id)
        
        # Получаем ответ от LLM с учетом истории
        response = self.llm_client.get_response(history)
        
        # Добавляем ответ ассистента в историю
        self.dialogue_manager.add_message(user_id, "assistant", response)
        
        # Отправляем ответ пользователю
        await message.answer(response)
    
    async def start(self):
        await self.dp.start_polling(self.bot)

