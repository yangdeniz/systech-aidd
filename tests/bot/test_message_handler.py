"""Тесты для MessageHandler."""

from unittest.mock import AsyncMock, Mock

import pytest

from src.bot.interfaces import DialogueStorage, LLMProvider, MediaProvider
from src.bot.message_handler import MessageHandler


@pytest.fixture
def mock_llm_provider() -> Mock:
    """Мок LLM провайдера."""
    mock = Mock(spec=LLMProvider)
    mock.get_response.return_value = "Test LLM response"
    return mock


@pytest.fixture
def mock_dialogue_storage() -> AsyncMock:
    """Мок хранилища диалогов."""
    mock = AsyncMock(spec=DialogueStorage)
    mock.add_message = AsyncMock(return_value=None)
    mock.get_history = AsyncMock(return_value=[])
    mock.clear_history = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_media_provider() -> AsyncMock:
    """Мок обработчика медиа."""
    mock = AsyncMock(spec=MediaProvider)
    mock.download_photo.return_value = b"fake_image_bytes"
    mock.photo_to_base64.return_value = "fake_base64_string"
    mock.download_audio.return_value = b"fake_audio_bytes"
    mock.transcribe_audio.return_value = "Fake transcribed text"
    return mock


def test_message_handler_initialization(
    mock_llm_provider: Mock, mock_dialogue_storage: Mock
) -> None:
    """Тест: инициализация MessageHandler без MediaProvider."""
    handler = MessageHandler(mock_llm_provider, mock_dialogue_storage)

    assert handler.llm_provider is mock_llm_provider
    assert handler.dialogue_storage is mock_dialogue_storage


def test_message_handler_with_media_provider(
    mock_llm_provider: Mock,
    mock_dialogue_storage: Mock,
    mock_media_provider: AsyncMock,
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
    mock_llm_provider: Mock, mock_dialogue_storage: AsyncMock
) -> None:
    """Тест: обработка текстового сообщения пользователя."""
    handler = MessageHandler(mock_llm_provider, mock_dialogue_storage)

    # Act
    response = await handler.handle_user_message(123, "testuser", "Hello")

    # Assert
    assert response == "Test LLM response"
    mock_dialogue_storage.add_message.assert_any_await(123, "user", "Hello")
    mock_dialogue_storage.add_message.assert_any_await(123, "assistant", "Test LLM response")
    mock_dialogue_storage.get_history.assert_awaited_once_with(123)
    mock_llm_provider.get_response.assert_called_once()


@pytest.mark.asyncio
async def test_handle_photo_message_with_caption(
    mock_llm_provider: Mock,
    mock_dialogue_storage: AsyncMock,
    mock_media_provider: AsyncMock,
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
    add_message_calls = mock_dialogue_storage.add_message.await_args_list
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
    mock_llm_provider: Mock,
    mock_dialogue_storage: AsyncMock,
    mock_media_provider: AsyncMock,
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
    add_message_calls = mock_dialogue_storage.add_message.await_args_list
    content = add_message_calls[0][0][2]

    assert isinstance(content, list)
    assert content[0]["type"] == "text"
    assert "фото" in content[0]["text"].lower() or "изображение" in content[0]["text"].lower()


@pytest.mark.asyncio
async def test_handle_photo_message_without_media_provider(
    mock_llm_provider: Mock, mock_dialogue_storage: AsyncMock
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
    mock_llm_provider: Mock,
    mock_dialogue_storage: AsyncMock,
    mock_media_provider: AsyncMock,
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


@pytest.mark.asyncio
async def test_handle_voice_message() -> None:
    """🔴 RED: Тест обработки голосового сообщения."""
    # Arrange - моки
    mock_llm = Mock(spec=LLMProvider)
    mock_llm.get_response.return_value = "Test voice response"

    mock_storage = AsyncMock(spec=DialogueStorage)
    mock_storage.add_message = AsyncMock(return_value=None)
    mock_storage.get_history = AsyncMock(return_value=[])

    mock_media = AsyncMock(spec=MediaProvider)
    mock_media.download_audio.return_value = b"fake_audio_bytes"
    mock_media.transcribe_audio.return_value = "Привет HomeGuru, как дела?"

    handler = MessageHandler(mock_llm, mock_storage, media_provider=mock_media)

    mock_bot = AsyncMock()

    # Act
    response = await handler.handle_voice_message(
        user_id=123, username="testuser", voice_file_id="voice123", bot=mock_bot
    )

    # Assert
    assert response == "Test voice response"

    # Проверяем скачивание и транскрибацию
    mock_media.download_audio.assert_called_once_with("voice123", mock_bot)
    mock_media.transcribe_audio.assert_called_once_with(b"fake_audio_bytes")

    # Проверяем что транскрибированный текст был добавлен как user сообщение
    add_message_calls = mock_storage.add_message.await_args_list
    assert len(add_message_calls) == 2  # user message + assistant response

    user_message_call = add_message_calls[0]
    assert user_message_call[0][0] == 123  # user_id
    assert user_message_call[0][1] == "user"  # role
    assert user_message_call[0][2] == "Привет HomeGuru, как дела?"  # transcribed text


@pytest.mark.asyncio
async def test_handle_voice_message_without_media_provider() -> None:
    """🔴 RED: Тест попытки обработать голосовое сообщение без MediaProvider."""
    # Arrange
    mock_llm = Mock(spec=LLMProvider)
    mock_storage = AsyncMock(spec=DialogueStorage)

    handler = MessageHandler(mock_llm, mock_storage)  # Без MediaProvider
    mock_bot = AsyncMock()

    # Act & Assert
    with pytest.raises(ValueError, match="MediaProvider"):
        await handler.handle_voice_message(
            user_id=123, username="testuser", voice_file_id="voice123", bot=mock_bot
        )


@pytest.mark.asyncio
async def test_handle_voice_message_transcription_error() -> None:
    """🔴 RED: Тест обработки ошибки транскрибации."""
    # Arrange
    mock_llm = Mock(spec=LLMProvider)
    mock_storage = AsyncMock(spec=DialogueStorage)

    mock_media = AsyncMock(spec=MediaProvider)
    mock_media.download_audio.return_value = b"fake_audio_bytes"
    mock_media.transcribe_audio.side_effect = Exception("Transcription failed")

    handler = MessageHandler(mock_llm, mock_storage, media_provider=mock_media)
    mock_bot = AsyncMock()

    # Act & Assert
    with pytest.raises(Exception, match="Transcription failed"):
        await handler.handle_voice_message(
            user_id=123, username="testuser", voice_file_id="voice123", bot=mock_bot
        )
