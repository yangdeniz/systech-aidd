"""
Pydantic модели для API контракта статистики.

Определяет структуру данных для обмена между backend и frontend.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class MetricCard(BaseModel):
    """
    Модель карточки метрики для дашборда.

    Отображает ключевой показатель с трендом изменения.
    """

    title: str = Field(..., description="Название метрики")
    value: str | int = Field(..., description="Значение метрики")
    change_percent: float = Field(
        ..., description="Процент изменения относительно предыдущего периода"
    )
    description: str = Field(..., description="Текстовое описание тренда")


class TimeSeriesPoint(BaseModel):
    """
    Точка данных для временного ряда.

    Используется для построения графика активности.
    """

    date: str = Field(..., description="Дата в ISO формате (YYYY-MM-DD)")
    value: int = Field(..., ge=0, description="Значение (количество сообщений/диалогов)")


class DialogueInfo(BaseModel):
    """
    Информация о диалоге пользователя.

    Используется для отображения последних диалогов.
    """

    user_id: int = Field(..., description="Telegram user ID")
    username: str | None = Field(None, description="Telegram username или None")
    message_count: int = Field(..., ge=0, description="Количество сообщений в диалоге")
    last_message_at: datetime = Field(..., description="Время последнего сообщения")


class TopUser(BaseModel):
    """
    Информация о топ пользователе по активности.

    Используется для отображения самых активных пользователей.
    """

    user_id: int = Field(..., description="Telegram user ID")
    username: str | None = Field(None, description="Telegram username или None")
    total_messages: int = Field(..., ge=0, description="Общее количество сообщений")
    dialogue_count: int = Field(..., ge=0, description="Количество диалогов (сессий)")


class StatsResponse(BaseModel):
    """
    Полный ответ API со статистикой для дашборда.

    Содержит все данные, необходимые для отображения дашборда:
    - 4 карточки метрик
    - Данные для графика активности
    - Список последних диалогов
    - Топ пользователей
    """

    metrics: list[MetricCard] = Field(..., description="4 карточки с ключевыми метриками")
    time_series: list[TimeSeriesPoint] = Field(..., description="Данные для графика активности")
    recent_dialogues: list[DialogueInfo] = Field(
        ..., max_length=10, description="Последние 10 диалогов"
    )
    top_users: list[TopUser] = Field(..., max_length=5, description="Топ-5 пользователей")

    class Config:
        json_schema_extra = {
            "example": {
                "metrics": [
                    {
                        "title": "Total Dialogues",
                        "value": 1234,
                        "change_percent": 12.5,
                        "description": "Trending up this month",
                    },
                    {
                        "title": "Active Users",
                        "value": 567,
                        "change_percent": -5.2,
                        "description": "Down 5% this period",
                    },
                    {
                        "title": "Avg Messages per Dialogue",
                        "value": "45.7",
                        "change_percent": 8.3,
                        "description": "Strong user retention",
                    },
                    {
                        "title": "Messages Today",
                        "value": 892,
                        "change_percent": 15.6,
                        "description": "Steady performance increase",
                    },
                ],
                "time_series": [
                    {"date": "2024-10-10", "value": 120},
                    {"date": "2024-10-11", "value": 145},
                    {"date": "2024-10-12", "value": 132},
                ],
                "recent_dialogues": [
                    {
                        "user_id": 123456789,
                        "username": "john_doe",
                        "message_count": 15,
                        "last_message_at": "2024-10-17T14:30:00Z",
                    }
                ],
                "top_users": [
                    {
                        "user_id": 987654321,
                        "username": "power_user",
                        "total_messages": 342,
                        "dialogue_count": 12,
                    }
                ],
            }
        }
