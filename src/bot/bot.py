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
        self.dp.message()(self.handle_message)
    
    async def cmd_start(self, message: Message):
        await message.answer(
            "Привет! Я AI-ассистент на базе LLM. "
            "Задай мне любой вопрос!\n\n"
            "Я помню контекст нашего диалога."
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

