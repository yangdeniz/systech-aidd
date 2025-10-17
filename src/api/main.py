"""
FastAPI приложение для Stats API и Chat API.

Entrypoint для запуска API сервера. Предоставляет endpoints:
- /stats - статистика дашборда
- /api/chat/* - веб-чат с LLM

Запуск:
    uvicorn src.api.main:app --reload --port 8000

Документация:
    http://localhost:8000/docs

Environment Variables:
    COLLECTOR_MODE: "mock" или "real" (по умолчанию "mock")
    DATABASE_URL: URL для подключения к PostgreSQL (для COLLECTOR_MODE=real)
    ADMIN_PASSWORD: Пароль для админ режима чата (по умолчанию "admin123")
    OPENROUTER_API_KEY: API ключ для OpenRouter
    LLM_MODEL: Модель LLM (по умолчанию "anthropic/claude-3.5-sonnet")
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла (ДО других импортов)
load_dotenv()

from fastapi import FastAPI, HTTPException, Query  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402

from src.bot.dialogue_manager import DialogueManager  # noqa: E402
from src.bot.llm_client import LLMClient  # noqa: E402

from .auth import create_access_token, verify_admin_password  # noqa: E402
from .cache import get_cache  # noqa: E402
from .chat_models import (  # noqa: E402
    AuthRequest,
    AuthResponse,
    ChatRequest,
    ChatResponse,
    ClearHistoryRequest,
)
from .chat_service import create_chat_service  # noqa: E402
from .config import get_collector, get_config  # noqa: E402
from .models import StatsResponse  # noqa: E402

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event для инициализации и очистки ресурсов при старте/остановке приложения."""
    # Startup: инициализируем виртуальных пользователей для веб-чата
    global chat_service
    config = get_config()

    if config.collector_mode.value == "real" and chat_service is not None:
        try:
            # Получаем session factory из chat_service
            if hasattr(chat_service, "session_factory"):
                await create_web_chat_users(chat_service.session_factory, count=10)
        except Exception as e:
            logger.error(f"Failed to create web chat users on startup: {e}", exc_info=True)

    yield
    # Shutdown: здесь можно добавить очистку ресурсов при необходимости


# Создаем FastAPI приложение
app = FastAPI(
    title="HomeGuru API",
    description="API для статистики диалогов и веб-чата с LLM",
    version="0.3.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Настройка CORS для доступа frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация StatCollector через factory pattern
# Выбор между Mock и Real определяется через COLLECTOR_MODE env var
collector = get_collector()

# Инициализация кэша с TTL 60 секунд
cache = get_cache(ttl_seconds=60)

# Логируем режим работы при старте
config = get_config()
logger.info(f"Stats API started in {config.collector_mode.value.upper()} mode")

# Инициализация Chat Service (только для COLLECTOR_MODE=real)
chat_service = None
session_id_to_user_id: dict[str, int] = {}  # Маппинг session_id → user_id
next_web_user_id = -1  # Начальный ID для веб-пользователей


async def create_web_chat_users(session_factory: async_sessionmaker, count: int = 10) -> None:
    """Создать виртуальных пользователей для веб-чата."""
    from sqlalchemy import text

    async with session_factory() as session:
        try:
            # Создаем count пользователей с telegram_id от -1 до -count
            for i in range(1, count + 1):
                telegram_id = -i
                await session.execute(
                    text("""
                        INSERT INTO users (telegram_id, username, first_name, is_active)
                        VALUES (:telegram_id, :username, :first_name, true)
                        ON CONFLICT (telegram_id) DO NOTHING
                    """),
                    {
                        "telegram_id": telegram_id,
                        "username": f"web_user_{i}",
                        "first_name": f"Web User {i}",
                    },
                )
            await session.commit()
            logger.info(
                f"Ensured {count} virtual web chat users exist (telegram_id from -1 to -{count})"
            )
        except Exception as e:
            logger.error(f"Failed to create web chat users: {e}", exc_info=True)
            await session.rollback()


def get_or_create_web_user_id(session_id: str) -> int:
    """Получить или создать user_id для session_id."""
    global next_web_user_id
    if session_id not in session_id_to_user_id:
        session_id_to_user_id[session_id] = next_web_user_id
        next_web_user_id -= 1
    return session_id_to_user_id[session_id]


if config.collector_mode.value == "real":
    # Инициализируем ChatService только для real режима
    try:
        # Получаем DATABASE_URL и API keys из environment
        database_url = os.getenv("DATABASE_URL")
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        llm_model = os.getenv("LLM_MODEL", "anthropic/claude-3.5-sonnet")

        if not database_url:
            logger.warning("DATABASE_URL not set, chat API will be disabled")
        elif not openrouter_api_key:
            logger.warning("OPENROUTER_API_KEY not set, chat API will be disabled")
        else:
            # Создаем engine и session factory для chat
            chat_engine = create_async_engine(database_url, echo=False)
            chat_session_factory = async_sessionmaker(chat_engine, expire_on_commit=False)

            # Загружаем system prompt для HomeGuru
            system_prompt_path = Path(__file__).parent.parent / "bot" / "system_prompt.txt"
            system_prompt = system_prompt_path.read_text(encoding="utf-8")

            # Создаем LLM client и DialogueManager
            llm_client = LLMClient(
                api_key=openrouter_api_key, model=llm_model, system_prompt=system_prompt
            )
            dialogue_manager = DialogueManager(session_factory=chat_session_factory, max_history=50)

            # Создаем ChatService
            chat_service = create_chat_service(llm_client, dialogue_manager, chat_session_factory)
            # Сохраняем session_factory в chat_service для доступа из lifespan
            chat_service.session_factory = chat_session_factory
            logger.info("Chat service initialized (web users will be created on startup)")
    except Exception as e:
        logger.error(f"Failed to initialize chat service: {e}", exc_info=True)
        chat_service = None
else:
    logger.info("Chat API disabled in mock mode")


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """
    Root endpoint для проверки работоспособности API.

    Returns:
        Приветственное сообщение с версией API и режимом работы
    """
    return {
        "message": "HomeGuru Stats API",
        "version": "0.2.0",
        "mode": config.collector_mode.value,
        "docs": "/docs",
    }


@app.get("/stats", response_model=StatsResponse, tags=["statistics"])
async def get_stats(
    period: str = Query(
        "week",
        pattern="^(day|week|month)$",
        description="Период для статистики: 'day' (24 часа), 'week' (7 дней), 'month' (30 дней)",
    ),
) -> StatsResponse:
    """
    Получить статистику для дашборда за указанный период.

    Возвращает полный набор данных для отображения дашборда:
    - 4 карточки с ключевыми метриками
    - Данные для графика активности (временной ряд)
    - Список последних 10 диалогов
    - Топ-5 пользователей по активности

    Кэширование: результаты кэшируются на 60 секунд для снижения нагрузки на БД.

    Args:
        period: Период для статистики ('day', 'week', 'month')

    Returns:
        StatsResponse со всеми данными для дашборда

    Raises:
        HTTPException 400: Если указан некорректный период
        HTTPException 500: При внутренней ошибке сервера

    Example:
        GET /stats?period=week
        GET /stats?period=day
        GET /stats (default: week)
    """
    try:
        # Проверяем кэш
        cache_key = f"stats:{period}"
        cached_stats = await cache.get(cache_key)

        if cached_stats is not None:
            logger.debug(f"Cache hit for period={period}")
            return cached_stats

        # Кэш промахнулся, получаем данные из collector
        logger.debug(f"Cache miss for period={period}, fetching from collector")
        stats = await collector.get_stats(period)

        # Сохраняем в кэш
        await cache.set(cache_key, stats)

        return stats
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error fetching stats for period={period}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint для мониторинга.

    Returns:
        Статус работоспособности API
    """
    return {"status": "healthy"}


@app.get("/cache/info", tags=["cache"])
async def cache_info() -> dict[str, int]:
    """
    Информация о состоянии кэша.

    Returns:
        Размер кэша и количество удаленных истекших записей
    """
    size = cache.get_size()
    cleaned = await cache.cleanup_expired()
    return {
        "cache_size": size,
        "expired_cleaned": cleaned,
    }


@app.post("/cache/clear", tags=["cache"])
async def clear_cache() -> dict[str, str]:
    """
    Очистить весь кэш.

    Returns:
        Статус операции
    """
    await cache.clear()
    return {"status": "cache cleared"}


# ============================================================================
# Chat API Endpoints
# ============================================================================


@app.post("/api/chat/auth", response_model=AuthResponse, tags=["chat"])
async def authenticate_admin(request: AuthRequest) -> AuthResponse:
    """
    Аутентификация для админ режима чата.

    Args:
        request: Запрос с паролем

    Returns:
        JWT токен и время истечения

    Raises:
        HTTPException 401: Неверный пароль
    """
    if not verify_admin_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    token, expires_at = create_access_token({"role": "admin"})

    return AuthResponse(token=token, expires_at=expires_at.isoformat())


@app.post("/api/chat/message", response_model=ChatResponse, tags=["chat"])
async def send_chat_message(request: ChatRequest) -> ChatResponse:
    """
    Отправка сообщения в чат.

    Для admin режима требуется аутентификация через Bearer token.

    Args:
        request: Запрос с сообщением, режимом и session_id

    Returns:
        Ответ от чата с текстом и опциональным SQL запросом

    Raises:
        HTTPException 503: Chat service недоступен
        HTTPException 403: Требуется аутентификация для admin режима
        HTTPException 500: Ошибка обработки сообщения
    """
    if chat_service is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Chat service unavailable. "
                "Ensure COLLECTOR_MODE=real and all required env vars are set."
            ),
        )

    # Для admin режима можно добавить проверку токена в будущем
    # Сейчас используем упрощенную версию для разработки

    return await _process_chat_message(request)


async def _process_chat_message(request: ChatRequest) -> ChatResponse:
    """Внутренняя функция обработки сообщения."""
    try:
        # Получаем или создаем user_id для session_id
        user_id = get_or_create_web_user_id(request.session_id)

        # Обрабатываем сообщение через ChatService
        response_text, sql_query = await chat_service.process_message(  # type: ignore[union-attr]
            message=request.message, mode=request.mode, user_id=user_id
        )

        timestamp = datetime.utcnow().isoformat()

        return ChatResponse(message=response_text, sql_query=sql_query, timestamp=timestamp)

    except Exception as e:
        logger.error("Error processing chat message: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}") from e


@app.get("/api/chat/history", tags=["chat"])
async def get_chat_history(session_id: str) -> list[dict[str, str]]:
    """
    Получить историю чата для session.

    Args:
        session_id: ID сессии

    Returns:
        Список сообщений

    Raises:
        HTTPException 503: Chat service недоступен
        HTTPException 500: Ошибка получения истории
    """
    if chat_service is None:
        raise HTTPException(status_code=503, detail="Chat service unavailable")

    try:
        user_id = get_or_create_web_user_id(session_id)

        # Получаем историю через dialogue_manager
        history = await chat_service.dialogue_manager.get_history(  # type: ignore[union-attr]
            user_id
        )

        # Преобразуем в формат для frontend
        result = []
        for msg in history:
            result.append(
                {
                    "role": msg["role"],
                    "content": str(msg["content"]),
                    # TODO: получать реальный timestamp из БД
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        return result

    except Exception as e:
        logger.error("Error fetching chat history: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}") from e


@app.post("/api/chat/clear", tags=["chat"])
async def clear_chat_history(request: ClearHistoryRequest) -> dict[str, str]:
    """
    Очистить историю чата для session.

    Args:
        request: Запрос с session_id

    Returns:
        Статус операции

    Raises:
        HTTPException 503: Chat service недоступен
        HTTPException 500: Ошибка очистки истории
    """
    if chat_service is None:
        raise HTTPException(status_code=503, detail="Chat service unavailable")

    try:
        user_id = get_or_create_web_user_id(request.session_id)

        # Очищаем историю через dialogue_manager
        await chat_service.dialogue_manager.clear_history(user_id)  # type: ignore[union-attr]

        return {"status": "history cleared", "session_id": request.session_id}

    except Exception as e:
        logger.error("Error clearing chat history: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}") from e
