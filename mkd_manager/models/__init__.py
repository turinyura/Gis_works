"""
Модели данных для приложения МКД-Менеджер
"""

from .building import Building
from .work import Work, WorkDependency, BuildingWork

# Экспортируем основные классы
__all__ = ["Building", "Work", "WorkDependency", "BuildingWork"]