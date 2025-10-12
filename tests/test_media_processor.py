"""Тесты для MediaProcessor и MediaProvider Protocol."""

import base64
from unittest.mock import AsyncMock, Mock

import pytest

from src.bot.interfaces import MediaProvider


def test_media_provider_protocol_compliance() -> None:
    """Тест: MediaProcessor должен соответствовать MediaProvider Protocol."""
    from src.bot.media_processor import MediaProcessor

    # Проверяем, что MediaProcessor реализует все методы Protocol
    processor: MediaProvider = MediaProcessor(whisper_model="base", whisper_device="cpu")

    # Проверяем наличие методов для фото
    assert hasattr(processor, "download_photo")
    assert hasattr(processor, "photo_to_base64")
    assert callable(processor.download_photo)
    assert callable(processor.photo_to_base64)

    # Проверяем наличие методов для аудио
    assert hasattr(processor, "download_audio")
    assert hasattr(processor, "transcribe_audio")
    assert callable(processor.download_audio)
    assert callable(processor.transcribe_audio)


def test_photo_to_base64() -> None:
    """Тест: конвертация bytes в base64 строку."""
    from src.bot.media_processor import MediaProcessor

    processor = MediaProcessor(whisper_model="base", whisper_device="cpu")

    # Arrange - тестовые байты изображения
    test_bytes = b"fake_image_data"

    # Act - конвертация в base64
    result = processor.photo_to_base64(test_bytes)

    # Assert - результат должен быть строкой в base64
    assert isinstance(result, str)
    assert result == base64.b64encode(test_bytes).decode("utf-8")


@pytest.mark.asyncio
async def test_download_photo() -> None:
    """Тест: скачивание фото через aiogram Bot."""
    from src.bot.media_processor import MediaProcessor

    processor = MediaProcessor(whisper_model="base", whisper_device="cpu")

    # Arrange - мок aiogram Bot
    mock_bot = AsyncMock()
    mock_file = Mock()
    mock_file.file_path = "photos/test_photo.jpg"
    mock_bot.get_file.return_value = mock_file

    # Мок для download_file
    test_photo_bytes = b"downloaded_image_data"
    mock_io = Mock()
    mock_io.read.return_value = test_photo_bytes
    mock_bot.download_file.return_value = mock_io

    # Act - скачивание фото
    result = await processor.download_photo("test_file_id", mock_bot)

    # Assert
    assert result == test_photo_bytes
    mock_bot.get_file.assert_called_once_with("test_file_id")
    mock_bot.download_file.assert_called_once_with("photos/test_photo.jpg")


@pytest.mark.asyncio
async def test_download_photo_error() -> None:
    """Тест: обработка ошибок при скачивании фото."""
    from src.bot.media_processor import MediaProcessor

    processor = MediaProcessor(whisper_model="base", whisper_device="cpu")

    # Arrange - мок Bot с ошибкой
    mock_bot = AsyncMock()
    mock_bot.get_file.side_effect = Exception("Telegram API error")

    # Act & Assert - должно пробросить исключение
    with pytest.raises(Exception, match="Telegram API error"):
        await processor.download_photo("invalid_file_id", mock_bot)


def test_media_processor_init_whisper() -> None:
    """🔴 RED: Тест инициализации MediaProcessor с Faster-Whisper."""
    from src.bot.media_processor import MediaProcessor

    # Act - создание процессора с параметрами Whisper
    processor = MediaProcessor(whisper_model="base", whisper_device="cpu")

    # Assert - проверяем что процессор создан и имеет whisper атрибут
    assert hasattr(processor, "whisper")
    assert processor.whisper is not None


@pytest.mark.asyncio
async def test_download_audio() -> None:
    """🔴 RED: Тест скачивания аудио через aiogram Bot."""
    from src.bot.media_processor import MediaProcessor

    processor = MediaProcessor(whisper_model="base", whisper_device="cpu")

    # Arrange - мок aiogram Bot
    mock_bot = AsyncMock()
    mock_file = Mock()
    mock_file.file_path = "voice/test_audio.ogg"
    mock_bot.get_file.return_value = mock_file

    # Мок для download_file
    test_audio_bytes = b"downloaded_audio_ogg_data"
    mock_io = Mock()
    mock_io.read.return_value = test_audio_bytes
    mock_bot.download_file.return_value = mock_io

    # Act - скачивание аудио
    result = await processor.download_audio("test_voice_file_id", mock_bot)

    # Assert
    assert result == test_audio_bytes
    mock_bot.get_file.assert_called_once_with("test_voice_file_id")
    mock_bot.download_file.assert_called_once_with("voice/test_audio.ogg")


@pytest.mark.asyncio
async def test_transcribe_audio() -> None:
    """🔴 RED: Тест транскрибации аудио через Faster-Whisper."""
    from unittest.mock import MagicMock, patch

    from src.bot.media_processor import MediaProcessor

    # Arrange - мокируем Faster-Whisper
    with patch("src.bot.media_processor.WhisperModel") as mock_whisper:
        mock_whisper_instance = MagicMock()

        # Мокируем результат транскрибации
        mock_segment = MagicMock()
        mock_segment.text = "Привет это тестовое голосовое сообщение"
        mock_info = MagicMock()
        mock_info.language = "ru"

        mock_whisper_instance.transcribe.return_value = ([mock_segment], mock_info)
        mock_whisper.return_value = mock_whisper_instance

        processor = MediaProcessor(whisper_model="base", whisper_device="cpu")

        # Act - транскрибация
        test_audio_bytes = b"fake_ogg_audio_data"
        result = await processor.transcribe_audio(test_audio_bytes)

        # Assert
        assert result == "Привет это тестовое голосовое сообщение"
        mock_whisper_instance.transcribe.assert_called_once()


@pytest.mark.asyncio
async def test_transcribe_audio_error_handling() -> None:
    """🔴 RED: Тест обработки ошибок при транскрибации."""
    from unittest.mock import MagicMock, patch

    from src.bot.media_processor import MediaProcessor

    # Arrange - мокируем Faster-Whisper с ошибкой
    with patch("src.bot.media_processor.WhisperModel") as mock_whisper:
        mock_whisper_instance = MagicMock()
        mock_whisper_instance.transcribe.side_effect = Exception("Whisper transcription error")
        mock_whisper.return_value = mock_whisper_instance

        processor = MediaProcessor(whisper_model="base", whisper_device="cpu")

        # Act & Assert - должно пробросить исключение
        test_audio_bytes = b"invalid_audio_data"
        with pytest.raises(Exception, match="Whisper transcription error"):
            await processor.transcribe_audio(test_audio_bytes)
