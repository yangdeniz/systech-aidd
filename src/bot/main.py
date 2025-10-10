import asyncio
from bot import TelegramBot
from config import Config


async def main():
    config = Config()
    telegram_bot = TelegramBot(config.telegram_token)
    await telegram_bot.start()


if __name__ == "__main__":
    asyncio.run(main())

