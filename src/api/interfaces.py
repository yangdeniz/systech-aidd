"""
Protocol интерфейсы для сборщиков статистики.

Определяет контракт для различных реализаций (Mock и Real).
Применяем DIP (Dependency Inversion Principle) через Protocol.
"""

from typing import Protocol

from .models import StatsResponse


class StatCollector(Protocol):
    """
    Интерфейс для сборщика статистики диалогов.

    Реализации:
    - MockStatCollector: генерирует тестовые данные
    - RealStatCollector: получает данные из БД (будет в F-Sprint-5)
    """

    async def get_stats(self, period: str) -> StatsResponse:
        """
        Получить статистику за указанный период.

        Args:
            period: Период для статистики ('day', 'week', 'month')

        Returns:
            StatsResponse с полными данными для дашборда

        Raises:
            ValueError: Если указан некорректный период
        """
        ...
