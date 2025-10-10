from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message


class TelegramBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self._register_handlers()
    
    def _register_handlers(self):
        self.dp.message(Command("start"))(self.cmd_start)
        self.dp.message()(self.echo_message)
    
    async def cmd_start(self, message: Message):
        await message.answer(
            "Привет! Я эхо-бот. Отправь мне любое сообщение, "
            "и я повторю его."
        )
    
    async def echo_message(self, message: Message):
        await message.answer(message.text)
    
    async def start(self):
        await self.dp.start_polling(self.bot)

