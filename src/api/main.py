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
from typing import Annotated

from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла (ДО других импортов)
load_dotenv()

from fastapi import Depends, FastAPI, HTTPException, Query  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402

from src.bot.dialogue_manager import DialogueManager  # noqa: E402
from src.bot.llm_client import LLMClient  # noqa: E402
from src.bot.models import User  # noqa: E402

from . import dependencies  # noqa: E402
from .auth import create_access_token, verify_admin_password  # noqa: E402
from .auth_models import (  # noqa: E402
    AuthResponse as WebAuthResponse,
)
from .auth_models import (
    LoginRequest,
    LogoutResponse,
    RegisterRequest,
    VerifyResponse,
)
from .auth_service import (  # noqa: E402
    authenticate_web_user,
    create_session_token,
    register_web_user,
    verify_session_token,
)
from .cache import get_cache  # noqa: E402
from .chat_models import (  # noqa: E402
    AuthRequest,
    AuthResponse,
    ChatRequest,
    ChatResponse,
)
from .chat_service import create_chat_service  # noqa: E402
from .config import get_collector, get_config  # noqa: E402
from .middleware import get_current_web_user, require_admin  # noqa: E402
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

# Инициализация Chat Service и Database Session Factory
chat_service = None
db_session_factory: async_sessionmaker | None = None  # Global database session factory
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
    # Инициализируем ChatService и Database Session Factory для real режима
    try:
        # Получаем DATABASE_URL и API keys из environment
        database_url = os.getenv("DATABASE_URL")
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        llm_model = os.getenv("LLM_MODEL", "anthropic/claude-3.5-sonnet")

        if not database_url:
            logger.warning("DATABASE_URL not set, database-dependent APIs will be disabled")
        else:
            # Создаем engine и GLOBAL session factory
            chat_engine = create_async_engine(database_url, echo=False)
            db_session_factory = async_sessionmaker(chat_engine, expire_on_commit=False)
            # Присваиваем session factory в dependencies модуль для использования в middleware
            dependencies.db_session_factory = db_session_factory
            logger.info("Database session factory initialized")

            # Создаем ChatService если есть OpenRouter API key
            if openrouter_api_key:
                # Загружаем system prompt для HomeGuru
                system_prompt_path = Path(__file__).parent.parent / "bot" / "system_prompt.txt"
                system_prompt = system_prompt_path.read_text(encoding="utf-8")

                # Создаем LLM client и DialogueManager
                llm_client = LLMClient(
                    api_key=openrouter_api_key, model=llm_model, system_prompt=system_prompt
                )
                dialogue_manager = DialogueManager(
                    session_factory=db_session_factory, max_history=50
                )

                # Создаем ChatService
                chat_service = create_chat_service(llm_client, dialogue_manager, db_session_factory)
                # Сохраняем session_factory в chat_service для доступа из lifespan
                chat_service.session_factory = db_session_factory
                logger.info("Chat service initialized (web users will be created on startup)")
            else:
                logger.warning("OPENROUTER_API_KEY not set, chat API will be disabled")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}", exc_info=True)
        chat_service = None
        db_session_factory = None
else:
    logger.info("Database-dependent APIs disabled in mock mode")


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
    _admin: Annotated[User, Depends(require_admin)] = None,  # type: ignore[assignment]
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
# Note: Database Session Dependency теперь в dependencies.py
# ============================================================================


# ============================================================================
# Web Auth API Endpoints
# ============================================================================


@app.post("/api/auth/register", response_model=WebAuthResponse, tags=["auth"])
async def register_user(
    request: RegisterRequest, session: Annotated[None, Depends(dependencies.get_db_session)]
) -> WebAuthResponse:
    """
    Регистрация нового пользователя.

    Args:
        request: Запрос с username, password, first_name

    Returns:
        JWT токен, expires_at, user_id, username, role

    Raises:
        HTTPException 400: Username занят или слабый пароль
        HTTPException 500: Внутренняя ошибка
    """
    try:
        # Создаем нового пользователя
        new_user = await register_web_user(
            username=request.username,
            password=request.password,
            first_name=request.first_name,
            session=session,
        )

        # Автоматический login - создаем токен
        token, expires_at = create_session_token(new_user)

        return WebAuthResponse(
            token=token,
            expires_at=expires_at.isoformat(),
            user_id=new_user.id,
            username=new_user.username or "",
            role=new_user.role.value if new_user.role else "user",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("Error registering user: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.post("/api/auth/login", response_model=WebAuthResponse, tags=["auth"])
async def login_user(
    request: LoginRequest, session: Annotated[None, Depends(dependencies.get_db_session)]
) -> WebAuthResponse:
    """
    Вход в систему.

    Args:
        request: Запрос с username и password

    Returns:
        JWT токен, expires_at, user_id, username, role

    Raises:
        HTTPException 401: Неверные credentials
        HTTPException 500: Внутренняя ошибка
    """
    try:
        # Аутентифицируем пользователя
        user = await authenticate_web_user(
            username=request.username, password=request.password, session=session
        )

        if user is None:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Создаем токен
        token, expires_at = create_session_token(user)

        return WebAuthResponse(
            token=token,
            expires_at=expires_at.isoformat(),
            user_id=user.id,
            username=user.username or "",
            role=user.role.value if user.role else "user",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error logging in user: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.get("/api/auth/verify", response_model=VerifyResponse, tags=["auth"])
async def verify_token(token: str = Query(..., description="JWT токен")) -> VerifyResponse:
    """
    Проверка JWT токена.

    Args:
        token: JWT токен

    Returns:
        Информация о валидности токена и пользователе

    Raises:
        HTTPException 401: Токен невалидный или истек
    """
    try:
        payload = verify_session_token(token)

        return VerifyResponse(
            valid=True,
            user_id=payload.get("user_id"),
            username=payload.get("username"),
            role=payload.get("role"),
        )

    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        return VerifyResponse(valid=False, user_id=None, username=None, role=None)


@app.post("/api/auth/logout", response_model=LogoutResponse, tags=["auth"])
async def logout_user() -> LogoutResponse:
    """
    Выход из системы.

    Фактически просто возвращает статус OK, клиент должен удалить токен из localStorage.

    Returns:
        Статус операции
    """
    return LogoutResponse(status="ok", message="Logged out successfully")


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
async def send_chat_message(
    request: ChatRequest,
    current_user: Annotated[User, Depends(get_current_web_user)],
) -> ChatResponse:
    """
    Отправка сообщения в чат.

    Требуется аутентификация через Bearer token.

    Args:
        request: Запрос с сообщением и режимом
        current_user: Авторизованный пользователь

    Returns:
        Ответ от чата с текстом и опциональным SQL запросом

    Raises:
        HTTPException 503: Chat service недоступен
        HTTPException 401: Не авторизован
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

    return await _process_chat_message(request, current_user.id)


async def _process_chat_message(request: ChatRequest, user_id: int) -> ChatResponse:
    """Внутренняя функция обработки сообщения."""
    try:
        # Обрабатываем сообщение через ChatService с реальным user_id
        response_text, sql_query = await chat_service.process_message(  # type: ignore[union-attr]
            message=request.message, mode=request.mode, user_id=user_id
        )

        timestamp = datetime.utcnow().isoformat()

        return ChatResponse(message=response_text, sql_query=sql_query, timestamp=timestamp)

    except Exception as e:
        logger.error("Error processing chat message: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}") from e


@app.get("/api/chat/history", tags=["chat"])
async def get_chat_history(
    current_user: Annotated[User, Depends(get_current_web_user)],
) -> list[dict[str, str]]:
    """
    Получить историю чата для авторизованного пользователя.

    Args:
        current_user: Авторизованный пользователь

    Returns:
        Список сообщений

    Raises:
        HTTPException 401: Не авторизован
        HTTPException 503: Chat service недоступен
        HTTPException 500: Ошибка получения истории
    """
    if chat_service is None:
        raise HTTPException(status_code=503, detail="Chat service unavailable")

    try:
        # Получаем историю через dialogue_manager для реального user_id
        history = await chat_service.dialogue_manager.get_history(  # type: ignore[union-attr]
            current_user.id
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
async def clear_chat_history(
    current_user: Annotated[User, Depends(get_current_web_user)],
) -> dict[str, str]:
    """
    Очистить историю чата для авторизованного пользователя.

    Args:
        current_user: Авторизованный пользователь

    Returns:
        Статус операции

    Raises:
        HTTPException 401: Не авторизован
        HTTPException 503: Chat service недоступен
        HTTPException 500: Ошибка очистки истории
    """
    if chat_service is None:
        raise HTTPException(status_code=503, detail="Chat service unavailable")

    try:
        # Очищаем историю через dialogue_manager для реального user_id
        await chat_service.dialogue_manager.clear_history(current_user.id)  # type: ignore[union-attr]

        return {"status": "history cleared", "user_id": str(current_user.id)}

    except Exception as e:
        logger.error("Error clearing chat history: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}") from e
