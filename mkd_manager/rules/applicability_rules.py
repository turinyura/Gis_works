"""
Правила проверки применимости работ к конкретному МКД
"""

from ..models.building import Building
from ..models.work import Work


def check_applicability(building: Building, work: Work) -> tuple[bool, str]:
    """
    Проверить применимость работы к конкретному МКД
    
    Args:
        building: Объект здания МКД
        work: Объект работы
        
    Returns:
        tuple[bool, str]: (применимо ли, причина)
    """
    
    # Проверка по категории работ
    if work.category.value == "elevator":
        # Работы по лифтам применимы только если есть лифты
        if not building.has_elevator:
            return False, f"Работа '{work.name}' не применима - в доме нет лифтов"
        
        # Если указано количество лифтов, проверяем их наличие
        if work.code in ["18", "19"] and building.elevator_count == 0:
            return False, f"Работа '{work.name}' не применима - в доме нет лифтов для обслуживания"
    
    elif work.category.value == "gas":
        # Работы по газовому хозяйству применимы только если есть газ
        if not building.has_gas:
            return False, f"Работа '{work.name}' не применима - в доме нет газового хозяйства"
    
    elif work.category.value == "garbage_chute":
        # Работы по мусоропроводу применимы только если есть мусоропровод
        if not building.has_garbage_chute:
            return False, f"Работа '{work.name}' не применима - в доме нет мусоропровода"
        if building.garbage_chute_count == 0:
            return False, f"Работа '{work.name}' не применима - в доме нет мусоропроводов"
    
    elif work.category.value == "content":  # Содержание общего имущества
        # Проверка по износу для работ по содержанию
        if work.min_wear and building.foundation_wear < work.min_wear:
            return False, f"Работа '{work.name}' не применима - износ фундамента ({building.foundation_wear}%) меньше минимального ({work.min_wear}%)"
            
    elif work.category.value == "repair":  # Текущий ремонт
        # Проверка по износу для работ по ремонту
        if work.min_wear:
            # Выбираем соответствующий параметр износа в зависимости от кода работы
            wear_value = _get_building_wear_by_work_code(building, work.code)
            if wear_value < work.min_wear:
                return False, f"Работа '{work.name}' не применима - износ элемента ({wear_value}%) меньше минимального ({work.min_wear}%) для выполнения ремонта"
    
    # Проверка требований ОСС (общего собрания собственников)
    if work.requires_oss:
        # В реальной системе здесь будет проверка наличия решения ОСС
        # Пока что предполагаем, что для большинства работ ОСС не требуется
        pass
    
    # Проверка по площади помещений
    if work.code in ["5", "6"]:  # Чердачное и подвальное помещения
        if work.code == "5" and building.attic_area == 0:
            return False, f"Работа '{work.name}' не применима - в доме нет чердачного помещения"
        if work.code == "6" and building.basement_area == 0:
            return False, f"Работа '{work.name}' не применима - в доме нет подвального помещения"
    
    # Если все проверки пройдены
    return True, f"Работа '{work.name}' применима к данному МКД"


def _get_building_wear_by_work_code(building: Building, work_code: str) -> float:
    """
    Получить значение износа здания по коду работы
    
    Args:
        building: Объект здания
        work_code: Код работы
        
    Returns:
        float: Значение износа для соответствующего элемента здания
    """
    # Сопоставление кодов работ с параметрами износа здания
    wear_mapping = {
        "1": building.foundation_wear,      # Фундамент
        "2": building.walls_wear,          # Несущие стены
        "3": building.walls_wear,          # Перегородки
        "4": building.walls_wear,          # Междуэтажные перекрытия
        "5": building.roof_wear,           # Чердачное перекрытие
        "6": building.roof_wear,           # Подвальное перекрытие
        "10": building.roof_wear,          # Кровля
        "11": building.walls_wear,         # Парапеты, ограждения балконов
        # Добавьте другие соответствия по мере необходимости
    }
    
    return wear_mapping.get(work_code, 0.0)


def calculate_work_volume(building: Building, work: Work) -> float:
    """
    Рассчитать объем работы для конкретного МКД
    
    Args:
        building: Объект здания МКД
        work: Объект работы
        
    Returns:
        float: Объем работы
    """
    # Логика расчета объема работы в зависимости от типа работы и характеристик здания
    volume = 0.0
    
    if work.unit == "м2":
        # Для работ, измеряемых в квадратных метрах
        if work.code in ["1", "2", "3", "4", "5", "6", "10"]:  # Работы по площадям
            if work.code == "1":  # Фундамент
                volume = building.total_area * 0.1  # Условный коэффициент
            elif work.code in ["2", "3"]:  # Стены
                volume = building.total_area * 0.7  # Условный коэффициент
            elif work.code in ["4", "5", "6"]:  # Перекрытия
                volume = building.total_area  # Площадь перекрытия приблизительно равна общей площади
            elif work.code == "10":  # Кровля
                volume = building.total_area  # Площадь кровли приблизительно равна общей площади
    
    elif work.unit == "шт":
        # Для работ, измеряемых в штуках
        if work.code == "18":  # Лифты
            volume = building.elevator_count
        elif work.code == "25":  # Пожарная сигнализация
            volume = 1  # Обычно одна система на дом
        elif work.code == "26":  # Система дымоудаления
            volume = 1  # Обычно одна система на дом
        # Добавьте другие виды работ в штуках
    
    elif work.unit == "м":
        # Для работ, измеряемых в погонных метрах
        if work.code in ["12", "13"]:  # Водосточная система, теплоизоляция труб
            volume = building.floors * building.entrances * 3  # Условный расчет
    
    # Применяем формулу расчета, если она определена для работы
    if work.formula:
        # Здесь можно реализовать более сложную логику вычисления объема по формуле
        pass
    
    return volume