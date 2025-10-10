import asyncio
import logging
from bot import TelegramBot
from llm_client import LLMClient
from dialogue_manager import DialogueManager
from config import Config


def setup_logging():
    """
    Настройка логирования: вывод в консоль и файл bot.log
    """
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Настраиваем корневой логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Обработчик для файла
    file_handler = logging.FileHandler('bot.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logging.info("Logging configured successfully")


async def main():
    setup_logging()
    
    logging.info("Starting bot initialization...")
    
    config = Config()
    
    # Создаем LLM клиент
    llm_client = LLMClient(
        api_key=config.openrouter_api_key,
        model=config.openrouter_model,
        system_prompt=config.system_prompt
    )
    logging.info("LLM client initialized")
    
    # Создаем менеджер диалогов
    dialogue_manager = DialogueManager(max_history=config.max_history)
    logging.info(f"Dialogue manager initialized with max_history={config.max_history}")
    
    # Создаем бота
    telegram_bot = TelegramBot(config.telegram_token, llm_client, dialogue_manager)
    logging.info("Telegram bot initialized")
    
    logging.info("Bot is starting polling...")
    await telegram_bot.start()


if __name__ == "__main__":
    asyncio.run(main())

