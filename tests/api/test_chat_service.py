"""
Тесты для ChatService.

Тестируем обработку сообщений в normal и admin режимах, text2sql pipeline,
валидацию SQL запросов и обработку ошибок.
"""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.api.chat_service import ChatService


@pytest.fixture
def mock_llm_client():
    """Mock LLM client."""
    mock = Mock()
    mock.get_response = Mock(return_value="Test LLM response")
    mock.model = "test-model"
    mock.client = Mock()
    mock.client.api_key = "test-key"
    return mock


@pytest.fixture
def mock_dialogue_manager():
    """Mock DialogueManager."""
    mock = AsyncMock()
    mock.add_message = AsyncMock()
    mock.get_history = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_session_factory():
    """Mock session factory."""
    return AsyncMock()


@pytest.fixture
def text2sql_prompt():
    """Test text2sql prompt."""
    return "Test prompt for text2sql conversion"


@pytest.fixture
def chat_service(mock_llm_client, mock_dialogue_manager, mock_session_factory, text2sql_prompt):
    """Create ChatService instance with mocks."""
    return ChatService(
        llm_client=mock_llm_client,
        dialogue_manager=mock_dialogue_manager,
        session_factory=mock_session_factory,
        text2sql_prompt=text2sql_prompt,
    )


class TestNormalMode:
    """Тесты для обычного режима."""

    @pytest.mark.asyncio
    async def test_process_normal_mode(self, chat_service, mock_llm_client, mock_dialogue_manager):
        """Тестируем обработку сообщения в normal режиме."""
        message = "Hello, how are you?"
        user_id = 123

        response, sql_query = await chat_service.process_message(message, "normal", user_id)

        # Проверяем что сообщение было сохранено
        assert mock_dialogue_manager.add_message.call_count == 2
        mock_dialogue_manager.add_message.assert_any_call(user_id, "user", message)
        mock_dialogue_manager.add_message.assert_any_call(user_id, "assistant", response)

        # Проверяем что LLM был вызван
        mock_llm_client.get_response.assert_called_once()

        # Проверяем что SQL запрос не возвращается в normal режиме
        assert sql_query is None

    @pytest.mark.asyncio
    async def test_normal_mode_with_history(self, chat_service, mock_dialogue_manager):
        """Тестируем что история используется при обработке."""
        message = "What about my previous question?"
        user_id = 456
        mock_dialogue_manager.get_history.return_value = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"},
        ]

        await chat_service.process_message(message, "normal", user_id)

        # Проверяем что история была запрошена
        mock_dialogue_manager.get_history.assert_called_once_with(user_id)


class TestAdminMode:
    """Тесты для админ режима."""

    @pytest.mark.asyncio
    async def test_process_admin_mode_success(self, chat_service):
        """Тестируем успешную обработку в admin режиме с text2sql."""
        message = "How many users do we have?"
        user_id = 789
        sql_query = "SELECT COUNT(*) FROM users"

        # Mock text2sql generation
        with patch.object(chat_service, "_text_to_sql", return_value=sql_query):
            # Mock SQL execution
            with patch.object(
                chat_service, "_execute_sql_query", return_value=[{"count": 42}]
            ) as mock_execute:
                response, returned_sql = await chat_service.process_message(
                    message, "admin", user_id
                )

                # Проверяем что SQL был выполнен
                mock_execute.assert_called_once_with(sql_query)

                # Проверяем что SQL запрос возвращается
                assert returned_sql == sql_query
                assert response is not None

    @pytest.mark.asyncio
    async def test_admin_mode_invalid_sql(self, chat_service):
        """Тестируем обработку невалидного SQL (не SELECT)."""
        message = "Delete all users"
        user_id = 999
        dangerous_sql = "DELETE FROM users"

        with patch.object(chat_service, "_text_to_sql", return_value=dangerous_sql):
            response, sql_query = await chat_service.process_message(message, "admin", user_id)

            # Проверяем что возвращается ошибка
            assert "Ошибка" in response or "запрещенные операции" in response
            assert sql_query == dangerous_sql

    @pytest.mark.asyncio
    async def test_admin_mode_no_sql_generated(self, chat_service):
        """Тестируем случай когда не удается сгенерировать SQL."""
        message = "Tell me a joke"
        user_id = 111

        with patch.object(chat_service, "_text_to_sql", return_value="NULL"):
            response, sql_query = await chat_service.process_message(message, "admin", user_id)

            # Проверяем что возвращается сообщение об ошибке
            assert "не могу преобразовать" in response.lower()

    @pytest.mark.asyncio
    async def test_admin_mode_sql_execution_error(self, chat_service):
        """Тестируем обработку ошибки выполнения SQL."""
        message = "Show me stats"
        user_id = 222
        sql_query = "SELECT * FROM nonexistent_table"

        with patch.object(chat_service, "_text_to_sql", return_value=sql_query):
            with patch.object(
                chat_service, "_execute_sql_query", side_effect=Exception("Table not found")
            ):
                response, returned_sql = await chat_service.process_message(
                    message, "admin", user_id
                )

                # Проверяем что возвращается ошибка
                assert "Ошибка" in response
                assert "Table not found" in response or "SQL" in response


class TestSQLValidation:
    """Тесты для валидации SQL запросов."""

    def test_validate_select_query(self, chat_service):
        """Тестируем что SELECT запросы проходят валидацию."""
        valid_sql = "SELECT * FROM users WHERE is_active = true"
        assert chat_service._validate_sql(valid_sql) is True

    def test_validate_select_with_join(self, chat_service):
        """Тестируем что сложные SELECT с JOIN проходят валидацию."""
        valid_sql = "SELECT u.username, COUNT(m.id) FROM users u JOIN messages m ON u.telegram_id = m.user_id GROUP BY u.username"
        assert chat_service._validate_sql(valid_sql) is True

    @pytest.mark.parametrize(
        "dangerous_sql",
        [
            "DELETE FROM users",
            "UPDATE users SET is_active = false",
            "DROP TABLE messages",
            "INSERT INTO users VALUES (1, 'hacker')",
            "ALTER TABLE users ADD COLUMN hacked boolean",
            "TRUNCATE TABLE messages",
            "CREATE TABLE malicious (id INT)",
            "GRANT ALL ON users TO hacker",
            "REVOKE SELECT ON messages FROM public",
        ],
    )
    def test_reject_dangerous_queries(self, chat_service, dangerous_sql):
        """Тестируем что опасные запросы отклоняются."""
        assert chat_service._validate_sql(dangerous_sql) is False

    def test_reject_non_select_query(self, chat_service):
        """Тестируем что не-SELECT запросы отклоняются."""
        invalid_sql = "SHOW TABLES"
        assert chat_service._validate_sql(invalid_sql) is False


class TestSQLCleaning:
    """Тесты для очистки SQL от markdown."""

    def test_clean_sql_with_markdown(self, chat_service):
        """Тестируем очистку SQL с markdown блоками."""
        sql_with_markdown = "```sql\nSELECT * FROM users\n```"
        cleaned = chat_service._clean_sql(sql_with_markdown)
        assert cleaned == "SELECT * FROM users"

    def test_clean_sql_without_markdown(self, chat_service):
        """Тестируем что чистый SQL не изменяется."""
        clean_sql = "SELECT * FROM messages"
        cleaned = chat_service._clean_sql(clean_sql)
        assert cleaned == clean_sql

    def test_clean_sql_with_extra_whitespace(self, chat_service):
        """Тестируем удаление лишних пробелов."""
        sql_with_spaces = "  \n  SELECT * FROM users  \n  "
        cleaned = chat_service._clean_sql(sql_with_spaces)
        assert cleaned == "SELECT * FROM users"


class TestSQLResultsFormatting:
    """Тесты для форматирования результатов SQL."""

    def test_format_empty_results(self, chat_service):
        """Тестируем форматирование пустых результатов."""
        results = []
        formatted = chat_service._format_sql_results(results, "SELECT * FROM users")
        assert "не вернул результатов" in formatted

    def test_format_single_count_result(self, chat_service):
        """Тестируем форматирование результата COUNT."""
        results = [{"count": 42}]
        formatted = chat_service._format_sql_results(results, "SELECT COUNT(*) as count FROM users")
        assert "count" in formatted
        assert "42" in formatted

    def test_format_multiple_results(self, chat_service):
        """Тестируем форматирование множественных результатов."""
        results = [
            {"id": 1, "username": "user1"},
            {"id": 2, "username": "user2"},
            {"id": 3, "username": "user3"},
        ]
        formatted = chat_service._format_sql_results(results, "SELECT * FROM users")
        assert "3" in formatted  # количество результатов
        assert "user1" in formatted
        assert "user2" in formatted

    def test_format_many_results_truncated(self, chat_service):
        """Тестируем что большое количество результатов обрезается."""
        results = [{"id": i, "username": f"user{i}"} for i in range(50)]
        formatted = chat_service._format_sql_results(results, "SELECT * FROM users")

        # Должны показаться только первые 20 и сообщение о дополнительных
        assert "20" in formatted or "user19" in formatted
        assert "еще" in formatted or "30" in formatted  # должно быть указание на оставшиеся 30
