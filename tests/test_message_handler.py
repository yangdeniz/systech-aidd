"""Тесты для MessageHandler."""

from unittest.mock import AsyncMock, Mock

import pytest

from src.bot.interfaces import DialogueStorage, LLMProvider, MediaProvider
from src.bot.message_handler import MessageHandler


@pytest.fixture
def mock_llm_provider() -> LLMProvider:
    """Мок LLM провайдера."""
    mock = Mock(spec=LLMProvider)
    mock.get_response.return_value = "Test LLM response"
    return mock


@pytest.fixture
def mock_dialogue_storage() -> DialogueStorage:
    """Мок хранилища диалогов."""
    mock = Mock(spec=DialogueStorage)
    mock.get_history.return_value = []
    return mock


@pytest.fixture
def mock_media_provider() -> MediaProvider:
    """Мок обработчика медиа."""
    mock = AsyncMock(spec=MediaProvider)
    mock.download_photo.return_value = b"fake_image_bytes"
    mock.photo_to_base64.return_value = "fake_base64_string"
    return mock


def test_message_handler_initialization(
    mock_llm_provider: LLMProvider, mock_dialogue_storage: DialogueStorage
) -> None:
    """Тест: инициализация MessageHandler без MediaProvider."""
    handler = MessageHandler(mock_llm_provider, mock_dialogue_storage)

    assert handler.llm_provider is mock_llm_provider
    assert handler.dialogue_storage is mock_dialogue_storage


def test_message_handler_with_media_provider(
    mock_llm_provider: LLMProvider,
    mock_dialogue_storage: DialogueStorage,
    mock_media_provider: MediaProvider,
) -> None:
    """Тест: инициализация MessageHandler с MediaProvider."""
    handler = MessageHandler(
        mock_llm_provider, mock_dialogue_storage, media_provider=mock_media_provider
    )

    assert handler.llm_provider is mock_llm_provider
    assert handler.dialogue_storage is mock_dialogue_storage
    assert handler.media_provider is mock_media_provider


@pytest.mark.asyncio
async def test_handle_user_message(
    mock_llm_provider: LLMProvider, mock_dialogue_storage: DialogueStorage
) -> None:
    """Тест: обработка текстового сообщения пользователя."""
    handler = MessageHandler(mock_llm_provider, mock_dialogue_storage)

    # Act
    response = await handler.handle_user_message(123, "testuser", "Hello")

    # Assert
    assert response == "Test LLM response"
    mock_dialogue_storage.add_message.assert_any_call(123, "user", "Hello")
    mock_dialogue_storage.add_message.assert_any_call(123, "assistant", "Test LLM response")
    mock_dialogue_storage.get_history.assert_called_once_with(123)
    mock_llm_provider.get_response.assert_called_once()


@pytest.mark.asyncio
async def test_handle_photo_message_with_caption(
    mock_llm_provider: LLMProvider,
    mock_dialogue_storage: DialogueStorage,
    mock_media_provider: MediaProvider,
) -> None:
    """Тест: обработка фото с подписью."""
    handler = MessageHandler(
        mock_llm_provider, mock_dialogue_storage, media_provider=mock_media_provider
    )

    # Arrange - мок aiogram Bot
    mock_bot = AsyncMock()

    # Act
    response = await handler.handle_photo_message(
        user_id=123,
        username="testuser",
        photo_file_id="photo123",
        caption="What's in this image?",
        bot=mock_bot,
    )

    # Assert
    assert response == "Test LLM response"

    # Проверяем скачивание и конвертацию
    mock_media_provider.download_photo.assert_called_once_with("photo123", mock_bot)
    mock_media_provider.photo_to_base64.assert_called_once_with(b"fake_image_bytes")

    # Проверяем что было добавлено мультимодальное сообщение
    add_message_calls = mock_dialogue_storage.add_message.call_args_list
    user_message_call = add_message_calls[0]

    assert user_message_call[0][0] == 123  # user_id
    assert user_message_call[0][1] == "user"  # role

    # content должен быть списком с текстом и изображением
    content = user_message_call[0][2]
    assert isinstance(content, list)
    assert len(content) == 2
    assert content[0]["type"] == "text"
    assert content[0]["text"] == "What's in this image?"
    assert content[1]["type"] == "image_url"
    assert "data:image/jpeg;base64,fake_base64_string" in content[1]["image_url"]["url"]


@pytest.mark.asyncio
async def test_handle_photo_message_without_caption(
    mock_llm_provider: LLMProvider,
    mock_dialogue_storage: DialogueStorage,
    mock_media_provider: MediaProvider,
) -> None:
    """Тест: обработка фото без подписи."""
    handler = MessageHandler(
        mock_llm_provider, mock_dialogue_storage, media_provider=mock_media_provider
    )

    mock_bot = AsyncMock()

    # Act - без caption
    response = await handler.handle_photo_message(
        user_id=123, username="testuser", photo_file_id="photo123", caption=None, bot=mock_bot
    )

    # Assert
    assert response == "Test LLM response"

    # Проверяем что текст по умолчанию добавлен
    add_message_calls = mock_dialogue_storage.add_message.call_args_list
    content = add_message_calls[0][0][2]

    assert isinstance(content, list)
    assert content[0]["type"] == "text"
    assert "фото" in content[0]["text"].lower() or "изображение" in content[0]["text"].lower()


@pytest.mark.asyncio
async def test_handle_photo_message_without_media_provider(
    mock_llm_provider: LLMProvider, mock_dialogue_storage: DialogueStorage
) -> None:
    """Тест: попытка обработать фото без MediaProvider."""
    handler = MessageHandler(mock_llm_provider, mock_dialogue_storage)

    mock_bot = AsyncMock()

    # Act & Assert - должно вызвать ошибку
    with pytest.raises(ValueError, match="MediaProvider"):
        await handler.handle_photo_message(
            user_id=123, username="testuser", photo_file_id="photo123", caption="Test", bot=mock_bot
        )


@pytest.mark.asyncio
async def test_handle_photo_message_error(
    mock_llm_provider: LLMProvider,
    mock_dialogue_storage: DialogueStorage,
    mock_media_provider: MediaProvider,
) -> None:
    """Тест: обработка ошибок при работе с фото."""
    handler = MessageHandler(
        mock_llm_provider, mock_dialogue_storage, media_provider=mock_media_provider
    )

    # Arrange - ошибка при скачивании
    mock_bot = AsyncMock()
    mock_media_provider.download_photo.side_effect = Exception("Download error")

    # Act & Assert
    with pytest.raises(Exception, match="Download error"):
        await handler.handle_photo_message(
            user_id=123, username="testuser", photo_file_id="photo123", caption="Test", bot=mock_bot
        )
