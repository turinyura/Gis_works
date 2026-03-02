from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date
from enum import Enum


class WorkCategory(str, Enum):
    CONTENT = "content"  # Содержание
    REPAIR = "repair"    # Текущий ремонт
    MANAGEMENT = "management"
    DISPATCH = "dispatch"
    CLEANING_TERRITORY = "cleaning_territory"
    CLEANING_MOP = "cleaning_mop"
    GARBAGE_CHUTE = "garbage_chute"
    ELEVATOR = "elevator"
    ELEVATOR_COMM = "elevator_comm"
    GAS = "gas"


class WorkType(str, Enum):
    PLANNED = "planned"
    EMERGENCY = "emergency"
    ON_REQUEST = "on_request"


class Work(SQLModel, table=True):
    __tablename__ = "works"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True)  # "20", "21", ...
    name: str
    category: WorkCategory
    work_type: WorkType
    periodicity: str  # "1 раз в год", "Ежемесячно"
    regulations: str  # Ссылки на нормативку
    unit: str  # Ед. измерения
    formula: Optional[str] = None  # Формула расчёта
    min_wear: Optional[float] = None  # Мин. износ для работы
    max_wear: Optional[float] = None  # Макс. износ
    requires_oss: bool = False  # Требуется ОСС
    critical: bool = False  # Критическая работа
    
    # Связи
    prerequisites: List["WorkDependency"] = Relationship(
        back_populates="work",
        sa_relationship_kwargs={"foreign_keys": "[WorkDependency.work_id]"}
    )
    dependents: List["WorkDependency"] = Relationship(
        back_populates="prerequisite_work",
        sa_relationship_kwargs={"foreign_keys": "[WorkDependency.prerequisite_work_id]"}
    )
    building_works: List["BuildingWork"] = Relationship(back_populates="work")


class WorkDependency(SQLModel, table=True):
    """Зависимости между работами (граф)"""
    __tablename__ = "work_dependencies"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    work_id: int = Field(foreign_key="works.id")
    prerequisite_work_id: int = Field(foreign_key="works.id")
    dependency_type: str  # "precedence", "resource", "logical"
    
    work: Work = Relationship(
        back_populates="prerequisites",
        sa_relationship_kwargs={"foreign_keys": "[WorkDependency.work_id]"}
    )
    prerequisite_work: Work = Relationship(
        back_populates="dependents",
        sa_relationship_kwargs={"foreign_keys": "[WorkDependency.prerequisite_work_id]"}
    )


class BuildingWork(SQLModel, table=True):
    """Привязка работ к конкретному МКД"""
    __tablename__ = "building_works"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    building_id: int = Field(foreign_key="buildings.id")
    work_id: int = Field(foreign_key="works.id")
    is_applicable: bool = True  # Применима ли работа к этому дому
    calculated_volume: float = 0  # Рассчитанный объём
    planned_volume: float = 0  # Запланированный объём
    actual_volume: float = 0  # Фактически выполненный
    unit_cost: float = 0  # Стоимость за единицу
    total_cost: float = 0  # Общая стоимость
    priority: int = 1  # Приоритет (1-высокий, 3-низкий)
    status: str = "planned"  # planned, in_progress, completed, cancelled
    scheduled_date: Optional[date] = None
    completed_date: Optional[date] = None
    
    building: "Building" = Relationship(back_populates="works")
    work: Work = Relationship(back_populates="building_works")