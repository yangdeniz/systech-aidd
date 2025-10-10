from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from llm_client import LLMClient


class TelegramBot:
    def __init__(self, token: str, llm_client: LLMClient):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.llm_client = llm_client
        self._register_handlers()
    
    def _register_handlers(self):
        self.dp.message(Command("start"))(self.cmd_start)
        self.dp.message()(self.handle_message)
    
    async def cmd_start(self, message: Message):
        await message.answer(
            "Привет! Я AI-ассистент на базе LLM. "
            "Задай мне любой вопрос!"
        )
    
    async def handle_message(self, message: Message):
        # Формируем запрос для LLM
        messages = [
            {"role": "user", "content": message.text}
        ]
        
        # Получаем ответ от LLM
        response = self.llm_client.get_response(messages)
        
        # Отправляем ответ пользователю
        await message.answer(response)
    
    async def start(self):
        await self.dp.start_polling(self.bot)

