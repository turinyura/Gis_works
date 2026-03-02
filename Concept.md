

## 🏗️ КОНЦЕПЦИЯ ПРИЛОЖЕНИЯ "МКД-Менеджер"

### 1. ЦЕЛЬ ПРИЛОЖЕНИЯ

Автоматизация планирования, структурирования и контроля работ по содержанию и ремонту МКД на основе:
- **Паспорта МКД** (характеристики здания)
- **Нормативных требований** (277 работ из перечня)
- **Логических связей** между работами (граф зависимостей)
- **Бюджетного распределения** (по ВСН 53-86р)

---

### 2. АРХИТЕКТУРА ПРИЛОЖЕНИЯ

```
┌─────────────────────────────────────────────────────────┐
│                    GUI (PyQt6/PySide6)                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │ Паспорт МКД │ │ Граф работ  │ │ Планирование &  │   │
│  │             │ │             │ │ Бюджет          │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────┐
│                    CORE LOGIC (Python)                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │ Критерии    │ │ Граф        │ │ Расчёт          │   │
│  │ применимости│ │ зависимостей│ │ бюджета         │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────┐
│                    DATA LAYER                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │ SQLite      │ │ JSON/YAML   │ │ NetworkX        │   │
│  │ (БД)        │ │ (Конфиги)   │ │ (Граф)          │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

### 3. ТЕХНОЛОГИЧЕСКИЙ СТЕК

| Компонент | Технология | Обоснование |
|-----------|-----------|-------------|
| **GUI** | PyQt6 / PySide6 | Профессиональный интерфейс, кроссплатформенность |
| **Графы** | NetworkX + Plotly | Визуализация зависимостей, интерактивность |
| **База данных** | SQLite + SQLModel | Лёгкость развёртывания, типизация |
| **Конфигурация** | YAML / JSON | Читаемость, версионирование |
| **Отчёты** | Jinja2 + PDF | Генерация документов |
| **Диаграммы** | Graphviz / Matplotlib | Визуализация графов работ |

---

### 4. С ЧЕГО НАЧНЁМ? (ПРИОРИТЕТЫ)

#### **ЭТАП 1: Модель данных (Фундамент)** ⭐⭐⭐

Создаём структуру данных для:
1. **Паспорта МКД** (30+ критериев)
2. **Перечня работ** (277 работ с атрибутами)
3. **Связей между работами** (граф зависимостей)

#### **ЭТАП 2: Логика применимости** ⭐⭐⭐

Реализуем движок, который:
- Фильтрует работы по критериям паспорта
- Рассчитывает объёмы по формулам
- Определяет приоритеты

#### **ЭТАП 3: Граф работ** ⭐⭐

Визуализируем:
- Зависимости между работами
- Последовательность выполнения
- Критический путь

#### **ЭТАП 4: GUI** ⭐⭐

Интерфейс для:
- Ввода данных паспорта
- Просмотра графа
- Планирования и отчётности

---

### 5. МОДЕЛЬ ДАННЫХ (НАЧАЛО)

```python
# models.py
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
    prerequisites: List["WorkDependency"] = Relationship(back_populates="work")
    building_works: List["BuildingWork"] = Relationship(back_populates="work")

class WorkDependency(SQLModel, table=True):
    """Зависимости между работами (граф)"""
    __tablename__ = "work_dependencies"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    work_id: int = Field(foreign_key="works.id")
    prerequisite_work_id: int = Field(foreign_key="works.id")
    dependency_type: str  # "precedence", "resource", "logical"
    
    work: Work = Relationship(back_populates="prerequisites")

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
    
    building: Building = Relationship(back_populates="works")
    work: Work = Relationship(back_populates="building_works")
```

---

### 6. ГРАФ ЗАВИСИМОСТЕЙ (ПРИМЕР)

```python
# graph_engine.py
import networkx as nx
import matplotlib.pyplot as plt

class WorkGraph:
    def __init__(self):
        self.G = nx.DiGraph()  # Направленный граф
    
    def add_work(self, work: Work):
        """Добавить работу в граф"""
        self.G.add_node(
            work.code,
            name=work.name,
            category=work.category,
            priority=work.critical
        )
    
    def add_dependency(self, work_code: str, prerequisite_code: str, type: str):
        """Добавить зависимость между работами"""
        self.G.add_edge(
            prerequisite_code,
            work_code,
            dependency_type=type
        )
    
    def get_execution_order(self):
        """Получить порядок выполнения работ (топологическая сортировка)"""
        return list(nx.topological_sort(self.G))
    
    def get_critical_path(self):
        """Найти критический путь"""
        # Реализация через longest_path для DAG
        pass
    
    def visualize(self, output_path: str = "work_graph.png"):
        """Визуализировать граф"""
        plt.figure(figsize=(20, 15))
        pos = nx.spring_layout(self.G, k=2, iterations=50)
        
        # Цвета по категориям
        category_colors = {
            'content': '#4CAF50',
            'repair': '#FF9800',
            'management': '#2196F3',
            'cleaning': '#9C27B0',
        }
        
        node_colors = [
            category_colors.get(
                self.G.nodes[node]['category'].value, 
                '#灰色'
            )
            for node in self.G.nodes()
        ]
        
        nx.draw(
            self.G, pos,
            node_color=node_colors,
            node_size=3000,
            with_labels=True,
            font_size=8,
            arrows=True,
            arrowsize=20
        )
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
```

---

### 7. ПРИМЕРЫ ЗАВИСИМОСТЕЙ МЕЖДУ РАБОТАМИ

```yaml
# dependencies.yaml
dependencies:
  # Осмотры должны предшествовать ремонтам
  - work: "136"  # Восстановление фундамента
    prerequisite: "21"  # Проверка фундамента
    type: "precedence"
    
  - work: "156"  # Ремонт кровли
    prerequisite: "46"  # Проверка кровли на протечки
    type: "precedence"
  
  # Сезонные зависимости
  - work: "149"  # Очистка кровли от снега
    prerequisite: "54"  # Проверка кровли на снег
    type: "logical"
  
  # Ресурсные зависимости
  - work: "170"  # Ремонт мусоропровода
    prerequisite: "75"  # Проверка мусоропровода
    type: "precedence"
  
  # Аварийные работы приоритетнее плановых
  - work: "154"  # Устранение протечек крыш
    prerequisite: null
    type: "emergency"  # Без зависимостей, выполняется немедленно
```

---

### 8. СТРУКТУРА ПРОЕКТА

```
mkd_manager/
├── main.py                 # Точка входа
├── config/
│   ├── settings.yaml       # Настройки приложения
│   ├── works.yaml          # Перечень 277 работ
│   └── dependencies.yaml   # Зависимости между работами
├── models/
│   ├── __init__.py
│   ├── work.py             # Модель работы
│   ├── building.py         # Паспорт МКД
│   └── database.py         # Настройка БД
├── core/
│   ├── __init__.py
│   ├── graph_engine.py     # Логика графов
│   ├── criteria_engine.py  # Проверка критериев применимости
│   ├── budget_engine.py    # Расчёт бюджета по ВСН
│   └── scheduler.py        # Планирование работ
├── gui/
│   ├── __init__.py
│   ├── main_window.py      # Главное окно
│   ├── passport_dialog.py  # Диалог паспорта МКД
│   ├── graph_widget.py     # Визуализация графа
│   └── report_widget.py    # Отчёты
├── database/
│   └── mkd.db              # SQLite БД
├── reports/
│   └── templates/          # Шаблоны отчётов
├── requirements.txt
└── README.md
```

---

### 9. ПЛАН РАЗРАБОТКИ (SPRINT'ы)

| Спринт | Длительность | Задачи | Результат |
|--------|-------------|--------|-----------|
| **1** | 2 недели | Модель данных, БД, загрузка 277 работ | Рабочая БД с работами |
| **2** | 2 недели | Паспорт МКД, критерии применимости | Фильтрация работ по дому |
| **3** | 2 недели | Граф зависимостей, визуализация | Интерактивный граф |
| **4** | 2 недели | Расчёт бюджета (ВСН 53-86р) | Распределение средств |
| **5** | 2 недели | GUI (основные экраны) | Рабочий интерфейс |
| **6** | 2 недели | Планирование, календарь | График работ |
| **7** | 2 недели | Отчёты, экспорт (PDF, Excel) | Готовые отчёты |
| **8** | 2 недели | Тестирование, оптимизация | Релиз v1.0 |

---

### 10. С ЧЕГО НАЧНЁМ ПРЯМО СЕЙЧАС? 🚀

**Предлагаю начать с создания базовой структуры проекта:**

```bash
# 1. Создать структуру папок
mkdir -p mkd_manager/{config,models,core,gui,database,reports/templates}

# 2. Создать requirements.txt
cat > requirements.txt << EOF
sqlmodel>=0.0.14
pyqt6>=6.6.0
networkx>=3.2
matplotlib>=3.8
plotly>=5.18
pyyaml>=6.0
jinja2>=3.1
reportlab>=4.0
EOF

# 3. Создать базовую модель данных (models/work.py, models/building.py)
# 4. Загрузить 277 работ из перечня в БД
# 5. Создать простой CLI для тестирования логики
```

---

## ❓ ВОПРОСЫ ДЛЯ УТОЧНЕНИЯ:

1. **Где будет работать приложение?**
   - Локально на компьютере специалиста УК?
   - Веб-приложение с доступом через браузер?
   - Гибридный вариант?

2. **Сколько МКД планируется обслуживать?**
   - 1-10 домов (SQLite достаточно)
   - 10-100 домов (PostgreSQL)
   - 100+ домов (Кластер БД)

3. **Нужна ли интеграция с внешними системами?**
   - 1С:УК?
   - ГИС ЖКХ?
   - Системы диспетчеризации?

4. **Кто будет пользователем?**
   - Технический специалист УК?
   - Руководитель УК?
   - Собственники (личный кабинет)?

---

**Давайте начнём с создания базовой структуры и модели данных. Готовы приступить к коду?** 🎯
