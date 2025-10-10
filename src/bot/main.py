import asyncio
from bot import TelegramBot
from llm_client import LLMClient
from dialogue_manager import DialogueManager
from config import Config


async def main():
    config = Config()
    
    # Создаем LLM клиент
    llm_client = LLMClient(
        api_key=config.openrouter_api_key,
        model=config.openrouter_model,
        system_prompt=config.system_prompt
    )
    
    # Создаем менеджер диалогов
    dialogue_manager = DialogueManager(max_history=config.max_history)
    
    # Создаем бота
    telegram_bot = TelegramBot(config.telegram_token, llm_client, dialogue_manager)
    await telegram_bot.start()


if __name__ == "__main__":
    asyncio.run(main())

