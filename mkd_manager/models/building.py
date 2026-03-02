from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from .work import BuildingWork


class Building(SQLModel, table=True):
    """Паспорт МКД"""
    __tablename__ = "buildings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    cadastral_number: str
    address: str
    year_built: int
    floors: int
    entrances: int
    total_area: float  # м²
    mop_area: float  # м² мест общего пользования
    territory_area: float  # м² придомовой территории
    
    # Критерии наличия (К01-К30+)
    has_elevator: bool = False
    elevator_count: int = 0
    has_garbage_chute: bool = False
    garbage_chute_count: int = 0
    has_basement: bool = False
    basement_area: float = 0
    has_attic: bool = False
    attic_area: float = 0
    has_gas: bool = False
    has_fire_alarm: bool = False
    has_heat_meter: bool = False
    # ... и так далее все 30+ критериев
    
    # Износ по элементам (для ВСН 53-86р)
    foundation_wear: float = 0
    walls_wear: float = 0
    roof_wear: float = 0
    engineering_wear: float = 0
    
    works: List["BuildingWork"] = Relationship(back_populates="building")