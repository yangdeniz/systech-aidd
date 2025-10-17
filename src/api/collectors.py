"""
Реализации сборщиков статистики.

MockStatCollector: генерирует реалистичные тестовые данные для разработки frontend.
RealStatCollector: реализация с интеграцией PostgreSQL для production использования.
"""

import random
from datetime import datetime, timedelta
from typing import Any

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


class RealStatCollector:
    """
    Реализация сборщика статистики с использованием PostgreSQL.

    Получает реальные данные из базы данных для дашборда статистики.
    Использует SQLAlchemy async ORM для выполнения запросов.

    Особенности:
    - Интеграция с существующими User и Message моделями
    - Оптимизированные SQL запросы с агрегацией
    - Поддержка различных периодов (day/week/month)
    - Возвращает данные в том же формате, что и MockStatCollector
    """

    def __init__(self, session_factory: Any) -> None:
        """
        Инициализация Real сборщика.

        Args:
            session_factory: Фабрика для создания async сессий SQLAlchemy
        """
        self.session_factory = session_factory

    async def get_stats(self, period: str) -> StatsResponse:
        """
        Получить реальную статистику за указанный период из базы данных.

        Args:
            period: Период для статистики ('day', 'week', 'month')

        Returns:
            StatsResponse с данными из БД

        Raises:
            ValueError: Если указан некорректный период
        """
        if period not in ("day", "week", "month"):
            raise ValueError(f"Invalid period: {period}. Must be 'day', 'week', or 'month'")

        async with self.session_factory() as session:
            # Импортируем модели здесь чтобы избежать циклических импортов
            from ..bot.models import Message, User

            # Собираем все данные
            metrics = await self._generate_metrics(session, User, Message, period)
            time_series = await self._generate_time_series(session, Message, period)
            recent_dialogues = await self._generate_recent_dialogues(session, User, Message)
            top_users = await self._generate_top_users(session, User, Message)

            return StatsResponse(
                metrics=metrics,
                time_series=time_series,
                recent_dialogues=recent_dialogues,
                top_users=top_users,
            )

    async def _generate_metrics(
        self,
        session: Any,
        User: Any,
        Message: Any,
        period: str,  # noqa: N803
    ) -> list[MetricCard]:
        """
        Генерирует 4 карточки метрик из базы данных.

        Args:
            session: Async сессия SQLAlchemy
            User: Модель пользователя (класс)
            Message: Модель сообщения (класс)
            period: Период для расчета метрик

        Returns:
            Список из 4 MetricCard
        """  # noqa: N803
        from sqlalchemy import func, select

        now = datetime.now()

        # Рассчитываем временной диапазон для текущего и предыдущего периодов
        period_deltas = {
            "day": timedelta(days=1),
            "week": timedelta(days=7),
            "month": timedelta(days=30),
        }
        current_period_start = now - period_deltas[period]
        previous_period_start = current_period_start - period_deltas[period]

        # 1. Total Dialogues - количество уникальных user_id с сообщениями
        current_dialogues = await session.scalar(
            select(func.count(func.distinct(Message.user_id)))
            .where(Message.created_at >= current_period_start)
            .where(Message.is_deleted == False)  # noqa: E712
        )
        previous_dialogues = await session.scalar(
            select(func.count(func.distinct(Message.user_id)))
            .where(Message.created_at >= previous_period_start)
            .where(Message.created_at < current_period_start)
            .where(Message.is_deleted == False)  # noqa: E712
        )
        dialogues_change = self._calculate_change_percent(
            current_dialogues or 0, previous_dialogues or 0
        )

        # 2. Active Users - количество активных пользователей
        active_users = await session.scalar(
            select(func.count()).select_from(User).where(User.is_active == True)  # noqa: E712
        )
        # Для изменения смотрим на количество пользователей, активных в предыдущем периоде
        previous_active = await session.scalar(
            select(func.count(func.distinct(Message.user_id)))
            .where(Message.created_at >= previous_period_start)
            .where(Message.created_at < current_period_start)
            .where(Message.is_deleted == False)  # noqa: E712
        )
        active_users_change = self._calculate_change_percent(
            active_users or 0, previous_active or 0
        )

        # 3. Avg Messages per Dialogue
        total_messages = await session.scalar(
            select(func.count())
            .select_from(Message)
            .where(Message.created_at >= current_period_start)
            .where(Message.is_deleted == False)  # noqa: E712
        )
        avg_messages = (total_messages or 0) / max(current_dialogues or 1, 1)

        # Для предыдущего периода
        prev_total_messages = await session.scalar(
            select(func.count())
            .select_from(Message)
            .where(Message.created_at >= previous_period_start)
            .where(Message.created_at < current_period_start)
            .where(Message.is_deleted == False)  # noqa: E712
        )
        prev_avg_messages = (prev_total_messages or 0) / max(previous_dialogues or 1, 1)
        avg_messages_change = self._calculate_change_percent(avg_messages, prev_avg_messages)

        # 4. Messages Today
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)

        messages_today = await session.scalar(
            select(func.count())
            .select_from(Message)
            .where(Message.created_at >= today_start)
            .where(Message.is_deleted == False)  # noqa: E712
        )
        messages_yesterday = await session.scalar(
            select(func.count())
            .select_from(Message)
            .where(Message.created_at >= yesterday_start)
            .where(Message.created_at < today_start)
            .where(Message.is_deleted == False)  # noqa: E712
        )
        messages_today_change = self._calculate_change_percent(
            messages_today or 0, messages_yesterday or 0
        )

        return [
            MetricCard(
                title="Total Dialogues",
                value=current_dialogues or 0,
                change_percent=round(dialogues_change, 1),
                description=self._get_trend_description(dialogues_change, "dialogues"),
            ),
            MetricCard(
                title="Active Users",
                value=active_users or 0,
                change_percent=round(active_users_change, 1),
                description=self._get_trend_description(active_users_change, "users"),
            ),
            MetricCard(
                title="Avg Messages per Dialogue",
                value=str(round(avg_messages, 1)),
                change_percent=round(avg_messages_change, 1),
                description=self._get_trend_description(avg_messages_change, "engagement"),
            ),
            MetricCard(
                title="Messages Today",
                value=messages_today or 0,
                change_percent=round(messages_today_change, 1),
                description=self._get_trend_description(messages_today_change, "activity"),
            ),
        ]

    async def _generate_time_series(
        self,
        session: Any,
        Message: Any,
        period: str,  # noqa: N803
    ) -> list[TimeSeriesPoint]:
        """
        Генерирует временной ряд для графика активности из базы данных.

        Args:
            session: Async сессия SQLAlchemy
            Message: Модель сообщения (класс)
            period: Период ('day' = 24 часа, 'week' = 7 дней, 'month' = 30 дней)

        Returns:
            Список TimeSeriesPoint с реальными данными
        """  # noqa: N803
        from sqlalchemy import func, select

        now = datetime.now()
        points: list[TimeSeriesPoint] = []

        if period == "day":
            # Последние 24 часа (почасовая разбивка)
            for i in range(24):
                hour_start = (now - timedelta(hours=23 - i)).replace(
                    minute=0, second=0, microsecond=0
                )
                hour_end = hour_start + timedelta(hours=1)

                count = await session.scalar(
                    select(func.count())
                    .select_from(Message)
                    .where(Message.created_at >= hour_start)
                    .where(Message.created_at < hour_end)
                    .where(Message.is_deleted == False)  # noqa: E712
                )

                points.append(
                    TimeSeriesPoint(
                        date=hour_start.strftime("%Y-%m-%d %H:00"),
                        value=count or 0,
                    )
                )

        elif period == "week":
            # Последние 7 дней (ежедневная разбивка)
            for i in range(7):
                day_start = (now - timedelta(days=6 - i)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                day_end = day_start + timedelta(days=1)

                count = await session.scalar(
                    select(func.count())
                    .select_from(Message)
                    .where(Message.created_at >= day_start)
                    .where(Message.created_at < day_end)
                    .where(Message.is_deleted == False)  # noqa: E712
                )

                points.append(
                    TimeSeriesPoint(
                        date=day_start.strftime("%Y-%m-%d"),
                        value=count or 0,
                    )
                )

        else:  # month
            # Последние 30 дней (ежедневная разбивка)
            for i in range(30):
                day_start = (now - timedelta(days=29 - i)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                day_end = day_start + timedelta(days=1)

                count = await session.scalar(
                    select(func.count())
                    .select_from(Message)
                    .where(Message.created_at >= day_start)
                    .where(Message.created_at < day_end)
                    .where(Message.is_deleted == False)  # noqa: E712
                )

                points.append(
                    TimeSeriesPoint(
                        date=day_start.strftime("%Y-%m-%d"),
                        value=count or 0,
                    )
                )

        return points

    async def _generate_recent_dialogues(
        self,
        session: Any,
        User: Any,
        Message: Any,  # noqa: N803
    ) -> list[DialogueInfo]:
        """
        Генерирует список последних 10 диалогов из базы данных.

        Args:
            session: Async сессия SQLAlchemy
            User: Модель пользователя (класс)
            Message: Модель сообщения (класс)

        Returns:
            Список из 10 DialogueInfo, отсортированных по времени
        """  # noqa: N803
        from sqlalchemy import func, select

        # Получаем последние 10 пользователей с их последними сообщениями и количеством
        subquery = (
            select(
                Message.user_id,
                func.max(Message.created_at).label("last_message_at"),
                func.count(Message.id).label("message_count"),
            )
            .where(Message.is_deleted == False)  # noqa: E712
            .group_by(Message.user_id)
            .order_by(func.max(Message.created_at).desc())
            .limit(10)
            .subquery()
        )

        # Джойним с User чтобы получить username
        query = (
            select(
                User.telegram_id,
                User.username,
                subquery.c.message_count,
                subquery.c.last_message_at,
            )
            .join(subquery, User.telegram_id == subquery.c.user_id)
            .order_by(subquery.c.last_message_at.desc())
        )

        result = await session.execute(query)
        rows = result.all()

        dialogues: list[DialogueInfo] = []
        for row in rows:
            dialogues.append(
                DialogueInfo(
                    user_id=row.telegram_id,
                    username=row.username,
                    message_count=row.message_count,
                    last_message_at=row.last_message_at,
                )
            )

        return dialogues

    async def _generate_top_users(self, session: Any, User: Any, Message: Any) -> list[TopUser]:  # noqa: N803
        """
        Генерирует топ-5 пользователей по активности из базы данных.

        Args:
            session: Async сессия SQLAlchemy
            User: Модель пользователя
            Message: Модель сообщения

        Returns:
            Список из 5 TopUser, отсортированных по total_messages
        """
        from sqlalchemy import func, select

        # Получаем топ-5 пользователей по количеству сообщений
        # Также считаем количество "диалогов" (уникальных дней с активностью)
        query = (
            select(
                User.telegram_id,
                User.username,
                func.count(Message.id).label("total_messages"),
                func.count(func.distinct(func.date(Message.created_at))).label("dialogue_count"),
            )
            .join(Message, User.telegram_id == Message.user_id)
            .where(Message.is_deleted == False)  # noqa: E712
            .group_by(User.telegram_id, User.username)
            .order_by(func.count(Message.id).desc())
            .limit(5)
        )

        result = await session.execute(query)
        rows = result.all()

        users: list[TopUser] = []
        for row in rows:
            users.append(
                TopUser(
                    user_id=row.telegram_id,
                    username=row.username,
                    total_messages=row.total_messages,
                    dialogue_count=row.dialogue_count,
                )
            )

        return users

    def _calculate_change_percent(self, current: float, previous: float) -> float:
        """
        Вычислить процент изменения.

        Args:
            current: Текущее значение
            previous: Предыдущее значение

        Returns:
            Процент изменения
        """
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100

    def _get_trend_description(self, change_percent: float, metric_type: str) -> str:
        """
        Получить описание тренда на основе процента изменения.

        Args:
            change_percent: Процент изменения
            metric_type: Тип метрики (dialogues, users, engagement, activity)

        Returns:
            Текстовое описание тренда
        """
        if change_percent > 15:
            descriptions = {
                "dialogues": "Strong growth this period",
                "users": "Growing user base",
                "engagement": "Excellent user retention",
                "activity": "High activity today",
            }
        elif change_percent > 5:
            descriptions = {
                "dialogues": "Steady increase",
                "users": "Stable growth",
                "engagement": "Good interaction rate",
                "activity": "Steady performance increase",
            }
        elif change_percent > -5:
            descriptions = {
                "dialogues": "Stable performance",
                "users": "Maintaining user base",
                "engagement": "Consistent engagement",
                "activity": "Normal fluctuation",
            }
        elif change_percent > -15:
            descriptions = {
                "dialogues": "Slight decline",
                "users": "Minor decrease",
                "engagement": "Needs attention",
                "activity": "Below average",
            }
        else:
            descriptions = {
                "dialogues": "Significant drop",
                "users": "Acquisition needs attention",
                "engagement": "Engagement declining",
                "activity": "Low activity",
            }

        return descriptions.get(metric_type, "Performance varies")
