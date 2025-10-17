"""
Сервис обработки чат-запросов.

Поддерживает два режима:
- Normal: обычное общение с LLM (HomeGuru)
- Admin: вопросы по статистике через text2sql pipeline
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.bot.dialogue_manager import DialogueManager
from src.bot.llm_client import LLMClient

logger = logging.getLogger(__name__)


class ChatService:
    """
    Сервис обработки чат-запросов с поддержкой normal и admin режимов.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        dialogue_manager: DialogueManager,
        session_factory: async_sessionmaker[AsyncSession],
        text2sql_prompt: str,
    ) -> None:
        """
        Инициализация сервиса.

        Args:
            llm_client: Клиент для работы с LLM
            dialogue_manager: Менеджер диалогов для хранения истории
            session_factory: Фабрика для создания сессий БД
            text2sql_prompt: System prompt для преобразования text → SQL
        """
        self.llm_client = llm_client
        self.dialogue_manager = dialogue_manager
        self.session_factory = session_factory
        self.text2sql_prompt = text2sql_prompt
        logger.info("ChatService initialized")

    async def process_message(
        self, message: str, mode: str, user_id: int
    ) -> tuple[str, str | None]:
        """
        Основной метод обработки сообщения.

        Args:
            message: Текст сообщения пользователя
            mode: Режим работы ("normal" или "admin")
            user_id: ID пользователя для хранения истории

        Returns:
            Tuple (response_text, sql_query)
            - response_text: ответ от LLM
            - sql_query: SQL запрос (только для admin mode, иначе None)
        """
        logger.info(f"Processing message in {mode} mode for user {user_id}")

        if mode == "normal":
            return await self._process_normal_mode(message, user_id)
        elif mode == "admin":
            return await self._process_admin_mode(message, user_id)
        else:
            raise ValueError(f"Invalid mode: {mode}")

    async def _process_normal_mode(self, message: str, user_id: int) -> tuple[str, None]:
        """
        Обработка обычного режима: общение с LLM.

        Pipeline:
        1. Получить историю диалога
        2. Добавить новое сообщение пользователя
        3. Отправить в LLM
        4. Сохранить ответ в историю
        5. Вернуть ответ

        Args:
            message: Сообщение пользователя
            user_id: ID пользователя

        Returns:
            Tuple (response, None)
        """
        # Сохраняем сообщение пользователя
        await self.dialogue_manager.add_message(user_id, "user", message)

        # Получаем историю для контекста
        history = await self.dialogue_manager.get_history(user_id)

        # Отправляем в LLM
        response = self.llm_client.get_response(history)

        # Сохраняем ответ ассистента
        await self.dialogue_manager.add_message(user_id, "assistant", response)

        logger.info(f"Normal mode: generated response length={len(response)} chars")
        return response, None

    async def _process_admin_mode(self, message: str, user_id: int) -> tuple[str, str]:
        """
        Обработка админ режима: text2sql → SQL → результат → LLM → ответ.

        Pipeline:
        1. Преобразовать вопрос в SQL через LLM с text2sql prompt
        2. Валидировать SQL (только SELECT)
        3. Выполнить SQL запрос
        4. Форматировать результаты
        5. Отправить результаты в LLM для генерации ответа
        6. Сохранить в историю
        7. Вернуть ответ + SQL

        Args:
            message: Вопрос пользователя
            user_id: ID пользователя

        Returns:
            Tuple (response, sql_query)
        """
        logger.info("Admin mode: starting text2sql pipeline")

        # Шаг 1: Преобразуем вопрос в SQL
        sql_query = await self._text_to_sql(message)

        # Если не удалось сгенерировать SQL (вопрос не связан с БД)
        if sql_query is None or sql_query.strip().upper() == "NULL":
            response = (
                "Извините, не могу преобразовать ваш вопрос в SQL запрос. "
                "Пожалуйста, задайте вопрос о статистике диалогов, "
                "пользователях или сообщениях."
            )
            await self.dialogue_manager.add_message(user_id, "user", message)
            await self.dialogue_manager.add_message(user_id, "assistant", response)
            return response, sql_query or ""

        # Шаг 2: Валидация SQL
        if not self._validate_sql(sql_query):
            error_msg = (
                "Ошибка: SQL запрос содержит запрещенные операции. Разрешены только SELECT запросы."
            )
            logger.warning("Invalid SQL query: %s", sql_query)
            await self.dialogue_manager.add_message(user_id, "user", message)
            await self.dialogue_manager.add_message(user_id, "assistant", error_msg)
            return error_msg, sql_query

        # Шаг 3: Выполняем SQL
        try:
            results = await self._execute_sql_query(sql_query)
        except Exception as e:
            error_msg = f"Ошибка выполнения SQL запроса: {str(e)}"
            logger.error(f"SQL execution error: {e}", exc_info=True)
            await self.dialogue_manager.add_message(user_id, "user", message)
            await self.dialogue_manager.add_message(user_id, "assistant", error_msg)
            return error_msg, sql_query

        # Шаг 4: Форматируем результаты для LLM
        formatted_results = self._format_sql_results(results, sql_query)

        # Шаг 5: Отправляем результаты в LLM для генерации ответа
        llm_prompt = f"""Пользователь задал вопрос: "{message}"

SQL запрос: {sql_query}

Результаты выполнения запроса:
{formatted_results}

Пожалуйста, сформулируй понятный ответ на вопрос пользователя на основе этих данных.
Ответ должен быть информативным, структурированным и легко читаемым.
"""

        # Получаем историю для контекста
        history = await self.dialogue_manager.get_history(user_id)
        history.append({"role": "user", "content": llm_prompt})

        response = self.llm_client.get_response(history)

        # Шаг 6: Сохраняем в историю
        await self.dialogue_manager.add_message(user_id, "user", message)
        await self.dialogue_manager.add_message(user_id, "assistant", response)

        logger.info(f"Admin mode: generated response with SQL query")
        return response, sql_query

    async def _text_to_sql(self, question: str) -> str | None:
        """
        Преобразование вопроса в SQL через LLM.

        Args:
            question: Вопрос пользователя на естественном языке

        Returns:
            SQL запрос или None если не удалось преобразовать
        """
        messages = [{"role": "user", "content": question}]

        # Создаем временный LLM клиент с text2sql prompt
        text2sql_client = LLMClient(
            api_key=self.llm_client.client.api_key,  # type: ignore[arg-type]
            model=self.llm_client.model,
            system_prompt=self.text2sql_prompt,
        )

        try:
            sql_query = text2sql_client.get_response(messages)
            # Очищаем от markdown если есть
            sql_query = self._clean_sql(sql_query)
            logger.debug(f"Generated SQL: {sql_query}")
            return sql_query
        except Exception as e:
            logger.error(f"Error generating SQL: {e}", exc_info=True)
            return None

    def _clean_sql(self, sql: str) -> str:
        """
        Очистка SQL от markdown и лишних символов.

        Args:
            sql: SQL запрос (возможно с markdown)

        Returns:
            Очищенный SQL
        """
        # Удаляем markdown блоки ```sql ... ```
        sql = re.sub(r"```sql\s*", "", sql)
        sql = re.sub(r"```\s*", "", sql)
        # Удаляем лишние пробелы
        sql = sql.strip()
        return sql

    def _validate_sql(self, sql: str) -> bool:
        """
        Валидация SQL запроса (только SELECT).

        Args:
            sql: SQL запрос для проверки

        Returns:
            True если запрос безопасный, False иначе
        """
        sql_upper = sql.upper().strip()

        # Проверяем что это SELECT
        if not sql_upper.startswith("SELECT"):
            return False

        # Запрещенные ключевые слова
        forbidden_keywords = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "ALTER",
            "TRUNCATE",
            "CREATE",
            "GRANT",
            "REVOKE",
        ]

        # Проверяем отсутствие запрещенных ключевых слов
        return all(keyword not in sql_upper for keyword in forbidden_keywords)

    async def _execute_sql_query(self, sql: str) -> list[dict[str, Any]]:
        """
        Выполнение SQL запроса.

        Args:
            sql: SQL запрос (только SELECT)

        Returns:
            Список результатов в виде словарей

        Raises:
            Exception: При ошибке выполнения запроса
        """
        async with self.session_factory() as session:
            result = await session.execute(text(sql))
            rows = result.fetchall()

            # Преобразуем Row объекты в словари
            if rows:
                columns = result.keys()
                return [dict(zip(columns, row, strict=False)) for row in rows]
            else:
                return []

    def _format_sql_results(self, results: list[dict[str, Any]], sql: str) -> str:
        """
        Форматирование результатов SQL для отправки в LLM.

        Args:
            results: Результаты выполнения SQL
            sql: Исходный SQL запрос

        Returns:
            Отформатированная строка с результатами
        """
        if not results:
            return "Запрос не вернул результатов."

        # Формируем читаемое представление
        formatted = f"Найдено результатов: {len(results)}\n\n"

        # Если результат один (например, COUNT)
        if len(results) == 1 and len(results[0]) == 1:
            key = list(results[0].keys())[0]
            value = results[0][key]
            formatted += f"{key}: {value}"
            return formatted

        # Если результатов много, показываем первые 20
        display_count = min(len(results), 20)
        for i, row in enumerate(results[:display_count], 1):
            formatted += f"\n{i}. "
            items = []
            for key, value in row.items():
                # Форматируем datetime
                if isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                items.append(f"{key}={value}")
            formatted += ", ".join(items)

        if len(results) > display_count:
            formatted += f"\n\n... и еще {len(results) - display_count} результатов"

        return formatted


def create_chat_service(
    llm_client: LLMClient,
    dialogue_manager: DialogueManager,
    session_factory: async_sessionmaker[AsyncSession],
) -> ChatService:
    """
    Factory функция для создания ChatService.

    Args:
        llm_client: LLM клиент
        dialogue_manager: Менеджер диалогов
        session_factory: Фабрика сессий БД

    Returns:
        Инициализированный ChatService
    """
    # Загружаем text2sql prompt
    prompt_path = Path(__file__).parent / "text2sql_prompt.txt"
    text2sql_prompt = prompt_path.read_text(encoding="utf-8")

    return ChatService(llm_client, dialogue_manager, session_factory, text2sql_prompt)
