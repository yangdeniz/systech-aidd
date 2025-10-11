"""Тесты для MediaProcessor и MediaProvider Protocol."""

import base64
from unittest.mock import AsyncMock, Mock

import pytest

from src.bot.interfaces import MediaProvider


def test_media_provider_protocol_compliance() -> None:
    """Тест: MediaProcessor должен соответствовать MediaProvider Protocol."""
    from src.bot.media_processor import MediaProcessor

    # Проверяем, что MediaProcessor реализует все методы Protocol
    processor: MediaProvider = MediaProcessor()

    # Проверяем наличие методов
    assert hasattr(processor, "download_photo")
    assert hasattr(processor, "photo_to_base64")
    assert callable(processor.download_photo)
    assert callable(processor.photo_to_base64)


def test_photo_to_base64() -> None:
    """Тест: конвертация bytes в base64 строку."""
    from src.bot.media_processor import MediaProcessor

    processor = MediaProcessor()

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

    processor = MediaProcessor()

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

    processor = MediaProcessor()

    # Arrange - мок Bot с ошибкой
    mock_bot = AsyncMock()
    mock_bot.get_file.side_effect = Exception("Telegram API error")

    # Act & Assert - должно пробросить исключение
    with pytest.raises(Exception, match="Telegram API error"):
        await processor.download_photo("invalid_file_id", mock_bot)
