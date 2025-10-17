"""
FastAPI приложение для Stats API.

Entrypoint для запуска API сервера. Предоставляет endpoint /stats
для получения статистики дашборда.

Запуск:
    uvicorn src.api.main:app --reload --port 8000

Документация:
    http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .collectors import MockStatCollector
from .models import StatsResponse

# Создаем FastAPI приложение
app = FastAPI(
    title="HomeGuru Stats API",
    description="API для получения статистики диалогов дашборда",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Настройка CORS для доступа frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация Mock сборщика статистики
# В F-Sprint-5 заменим на RealStatCollector с подключением к БД
collector = MockStatCollector()


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """
    Root endpoint для проверки работоспособности API.

    Returns:
        Приветственное сообщение с версией API
    """
    return {
        "message": "HomeGuru Stats API",
        "version": "0.1.0",
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
        stats = await collector.get_stats(period)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint для мониторинга.

    Returns:
        Статус работоспособности API
    """
    return {"status": "healthy"}
