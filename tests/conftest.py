from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.bot.command_handler import CommandHandler
from src.bot.dialogue_manager import DialogueManager
from src.bot.interfaces import DialogueStorage, LLMProvider, MediaProvider
from src.bot.message_handler import MessageHandler
from src.bot.models import Base


@pytest.fixture(scope="session")
def postgres_container():
    """Создает PostgreSQL контейнер для всей сессии тестов"""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture
async def test_engine(postgres_container):
    """Создает тестовый PostgreSQL engine через testcontainers"""
    # Конвертируем URL из psycopg2 в asyncpg
    database_url = postgres_container.get_connection_url().replace("psycopg2", "asyncpg")
    engine = create_async_engine(database_url, echo=False)

    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Очищаем таблицы после каждого теста
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_session_factory(test_engine):
    """Создает session factory для тестов"""
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def dialogue_manager(test_session_factory) -> DialogueStorage:
    """Создает DialogueManager для тестов"""
    # Создаем тестовых пользователей для предотвращения foreign key errors
    from src.bot.repository import UserRepository

    async with test_session_factory() as session:
        user_repo = UserRepository(session)
        # Создаем несколько тестовых пользователей с распространенными ID
        test_user_ids = [111, 123, 222, 456, 789, 12345]
        for user_id in test_user_ids:
            await user_repo.get_or_create_user(
                telegram_id=user_id,
                username=f"testuser{user_id}",
                first_name="Test",
                last_name="User",
                language_code="en",
            )

    return DialogueManager(session_factory=test_session_factory, max_history=20)


@pytest.fixture
def mock_llm_client() -> LLMProvider:
    """Создает мокированный LLMProvider"""
    mock = Mock(spec=LLMProvider)
    mock.get_response.return_value = "Test response from LLM"
    return mock


@pytest.fixture
def message_handler(
    mock_llm_client: LLMProvider, dialogue_manager: DialogueStorage
) -> MessageHandler:
    """Создает MessageHandler для тестов"""
    return MessageHandler(mock_llm_client, dialogue_manager)


@pytest.fixture
def command_handler(dialogue_manager: DialogueStorage) -> CommandHandler:
    """Создает CommandHandler для тестов"""
    return CommandHandler(dialogue_manager)


@pytest.fixture
def mock_message() -> AsyncMock:
    """Создает мокированное Telegram Message"""
    message = AsyncMock()
    message.from_user = Mock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.from_user.first_name = "Test"
    message.from_user.last_name = "User"
    message.from_user.language_code = "en"
    message.text = "Test message"
    message.answer = AsyncMock()
    return message


@pytest.fixture
def mock_bot_token() -> str:
    """Возвращает тестовый токен бота"""
    return "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"


@pytest.fixture
def mock_media_provider() -> MediaProvider:
    """Создает мокированный MediaProvider"""
    mock = AsyncMock(spec=MediaProvider)
    mock.download_photo.return_value = b"fake_image_bytes"
    mock.photo_to_base64.return_value = "fake_base64_string"
    mock.download_audio.return_value = b"fake_audio_bytes"
    mock.transcribe_audio.return_value = "Fake transcribed text"
    return mock


@pytest.fixture
def message_handler_with_media(
    mock_llm_client: LLMProvider,
    dialogue_manager: DialogueStorage,
    mock_media_provider: MediaProvider,
) -> MessageHandler:
    """Создает MessageHandler с MediaProvider для тестов"""
    return MessageHandler(mock_llm_client, dialogue_manager, media_provider=mock_media_provider)


@pytest.fixture
def telegram_bot(
    mock_bot_token: str,
    message_handler: MessageHandler,
    command_handler: CommandHandler,
    test_session_factory: async_sessionmaker[AsyncSession],
):  # type: ignore[misc]
    """Создает TelegramBot для тестов"""
    from src.bot.bot import TelegramBot

    return TelegramBot(mock_bot_token, message_handler, command_handler, test_session_factory)
