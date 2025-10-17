"""
Реализации сборщиков статистики.

MockStatCollector: генерирует реалистичные тестовые данные для разработки frontend.
RealStatCollector: будет реализован в F-Sprint-5 для работы с PostgreSQL.
"""

import random
from datetime import datetime, timedelta

from .models import DialogueInfo, MetricCard, StatsResponse, TimeSeriesPoint, TopUser


class MockStatCollector:
    """
    Mock реализация сборщика статистики с генерацией тестовых данных.

    Генерирует реалистичные данные для разработки и тестирования frontend
    без необходимости подключения к БД.

    Особенности:
    - Разные данные для разных периодов (day/week/month)
    - Правдоподобные временные ряды с трендами
    - Различные usernames и ID пользователей
    - Реалистичные метрики с процентами изменения
    """

    # Примеры usernames для генерации тестовых данных
    _SAMPLE_USERNAMES = [
        "john_doe",
        "interior_lover",
        "design_fan",
        "home_stylist",
        "anna_decor",
        "mike_designer",
        "sarah_home",
        None,  # Некоторые пользователи без username
        "architect_pro",
        "cozy_spaces",
        "modern_home",
        "vintage_style",
    ]

    def __init__(self) -> None:
        """Инициализация Mock сборщика."""
        # Используем seed для воспроизводимости данных в тестах
        random.seed(42)

    async def get_stats(self, period: str) -> StatsResponse:
        """
        Получить мок-статистику за указанный период.

        Args:
            period: Период для статистики ('day', 'week', 'month')

        Returns:
            StatsResponse с тестовыми данными

        Raises:
            ValueError: Если указан некорректный период
        """
        if period not in ("day", "week", "month"):
            raise ValueError(f"Invalid period: {period}. Must be 'day', 'week', or 'month'")

        return StatsResponse(
            metrics=self._generate_metrics(period),
            time_series=self._generate_time_series(period),
            recent_dialogues=self._generate_recent_dialogues(),
            top_users=self._generate_top_users(),
        )

    def _generate_metrics(self, period: str) -> list[MetricCard]:
        """
        Генерирует 4 карточки метрик.

        Args:
            period: Период для расчета метрик

        Returns:
            Список из 4 MetricCard
        """
        # Базовые значения меняются в зависимости от периода
        period_multipliers = {"day": 1, "week": 7, "month": 30}
        multiplier = period_multipliers[period]

        base_dialogues = 150 * multiplier
        base_users = 50 * multiplier
        base_messages_today = 892

        return [
            MetricCard(
                title="Total Dialogues",
                value=base_dialogues + random.randint(-50, 100),
                change_percent=round(random.uniform(-20, 25), 1),
                description=random.choice(
                    [
                        "Trending up this month",
                        "Strong growth",
                        "Steady increase",
                        "Down this period",
                    ]
                ),
            ),
            MetricCard(
                title="Active Users",
                value=base_users + random.randint(-20, 50),
                change_percent=round(random.uniform(-15, 20), 1),
                description=random.choice(
                    [
                        "Down 20% this period",
                        "Growing user base",
                        "Acquisition needs attention",
                        "Stable performance",
                    ]
                ),
            ),
            MetricCard(
                title="Avg Messages per Dialogue",
                value=str(round(random.uniform(40, 55), 1)),
                change_percent=round(random.uniform(-10, 15), 1),
                description=random.choice(
                    [
                        "Strong user retention",
                        "Engagement exceed targets",
                        "Good interaction rate",
                        "Needs improvement",
                    ]
                ),
            ),
            MetricCard(
                title="Messages Today",
                value=base_messages_today + random.randint(-100, 200),
                change_percent=round(random.uniform(-5, 20), 1),
                description=random.choice(
                    [
                        "Steady performance increase",
                        "Meets growth projections",
                        "High activity today",
                        "Normal fluctuation",
                    ]
                ),
            ),
        ]

    def _generate_time_series(self, period: str) -> list[TimeSeriesPoint]:
        """
        Генерирует временной ряд для графика активности.

        Args:
            period: Период ('day' = 24 часа, 'week' = 7 дней, 'month' = 30 дней)

        Returns:
            Список TimeSeriesPoint с трендом
        """
        now = datetime.now()
        points: list[TimeSeriesPoint] = []

        if period == "day":
            # Последние 24 часа (почасовая разбивка)
            for i in range(24):
                date_time = now - timedelta(hours=23 - i)
                # Имитация дневной активности (больше днем, меньше ночью)
                hour = date_time.hour
                base_value = 30 if 9 <= hour <= 21 else 10
                value = base_value + random.randint(-10, 15)
                points.append(
                    TimeSeriesPoint(date=date_time.strftime("%Y-%m-%d %H:00"), value=max(0, value))
                )

        elif period == "week":
            # Последние 7 дней (ежедневная разбивка)
            for i in range(7):
                date = now - timedelta(days=6 - i)
                # Имитация недельного тренда с ростом
                base_value = 150 + i * 20
                value = base_value + random.randint(-30, 40)
                points.append(TimeSeriesPoint(date=date.strftime("%Y-%m-%d"), value=value))

        else:  # month
            # Последние 30 дней (ежедневная разбивка)
            for i in range(30):
                date = now - timedelta(days=29 - i)
                # Имитация месячного тренда с волнами
                base_value = 120 + (i % 7) * 15  # Недельные циклы
                value = base_value + random.randint(-25, 35)
                points.append(TimeSeriesPoint(date=date.strftime("%Y-%m-%d"), value=value))

        return points

    def _generate_recent_dialogues(self) -> list[DialogueInfo]:
        """
        Генерирует список последних 10 диалогов.

        Returns:
            Список из 10 DialogueInfo, отсортированных по времени
        """
        dialogues: list[DialogueInfo] = []
        now = datetime.now()

        for i in range(10):
            user_id = random.randint(100000000, 999999999)
            username = random.choice(self._SAMPLE_USERNAMES)
            message_count = random.randint(5, 50)
            # Последние диалоги за последние несколько часов/дней
            hours_ago = i * random.randint(1, 4)
            last_message_at = now - timedelta(hours=hours_ago)

            dialogues.append(
                DialogueInfo(
                    user_id=user_id,
                    username=username,
                    message_count=message_count,
                    last_message_at=last_message_at,
                )
            )

        return dialogues

    def _generate_top_users(self) -> list[TopUser]:
        """
        Генерирует топ-5 пользователей по активности.

        Returns:
            Список из 5 TopUser, отсортированных по total_messages
        """
        users: list[TopUser] = []

        # Генерируем топ пользователей с убывающей активностью
        base_messages = 350
        for i in range(5):
            user_id = random.randint(100000000, 999999999)
            username = random.choice(self._SAMPLE_USERNAMES)
            total_messages = base_messages - i * 50 + random.randint(-20, 20)
            dialogue_count = random.randint(8, 20)

            users.append(
                TopUser(
                    user_id=user_id,
                    username=username,
                    total_messages=total_messages,
                    dialogue_count=dialogue_count,
                )
            )

        # Сортируем по убыванию total_messages
        users.sort(key=lambda u: u.total_messages, reverse=True)
        return users
