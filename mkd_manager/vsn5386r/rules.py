"""
Правила ВСН 53-86р для определения необходимости ремонтных работ
Единые нормы предельных износов элементов жилых зданий
"""

class VSN5386Rules:
    """
    Класс, содержащий правила из ВСН 53-86р для определения необходимости ремонтных работ
    на основе износа элементов здания.
    """
    
    def __init__(self):
        """
        Инициализирует правила ВСН 53-86р.
        """
        # Нормативные значения предельного износа для различных элементов здания (%)
        self.wear_limits = {
            # Фундамент
            'foundation': {
                'stone_concrete': 75,  # Каменный или бетонный фундамент
                'precast_concrete': 75,  # Сборный бетонный фундамент
                'wooden': 50,  # Деревянный фундамент
                'pile': 75  # Свайный фундамент
            },
            
            # Стены
            'walls': {
                'stone_brick': 70,  # Каменные или кирпичные стены
                'large_block': 70,  # Крупноблочные стены
                'large_panel': 70,  # Крупнопанельные стены
                'wooden_frame': 50,  # Деревянные каркасные стены
                'log_wall': 50  # Срубовые стены
            },
            
            # Перекрытия
            'floors': {
                'wooden': 70,  # Деревянные перекрытия
                'concrete': 75,  # Железобетонные перекрытия
                'mixed': 70  # Смешанные перекрытия
            },
            
            # Кровля
            'roof': {
                'soft_roof': 65,  # Гибкая (рулонная) кровля
                'tile_roof': 70,  # Черепичная кровля
                'metal_roof': 70,  # Металлическая кровля
                'asbestos_cement_roof': 65  # Асбестоцементная кровля
            },
            
            # Фасады
            'facade': {
                'plastered': 60,  # Оштукатуренные фасады
                'cladding': 65,  # Облицованные фасады
                'painting': 50  # Крашеные фасады
            },
            
            # Инженерные системы
            'engineering_systems': {
                'water_supply': 75,  # Водоснабжение
                'sewerage': 75,  # Канализация
                'heating': 75,  # Отопление
                'gas_supply': 75,  # Газоснабжение
                'electrical': 75,  # Электроснабжение
                'ventilation': 70,  # Вентиляция
                'elevator': 65,  # Лифты
                'fire_safety': 65  # Системы пожарной безопасности
            }
        }
        
        # Типы ремонтов в зависимости от степени износа
        self.repair_types = {
            'routine_maintenance': (0, 25),  # Текущее содержание
            'minor_repair': (25, 50),  # Мелкий ремонт
            'major_repair': (50, 75),  # Капитальный ремонт
            'reconstruction': (75, 100)  # Реконструкция
        }

    def get_wear_limit(self, element_type: str, construction_type: str) -> float:
        """
        Получить предельный износ для конкретного элемента и типа конструкции.

        :param element_type: Тип элемента ('foundation', 'walls', 'floors', 'roof', 'facade', 'engineering_systems')
        :param construction_type: Тип конструкции (например, 'stone_concrete', 'wooden' и т.д.)
        :return: Предельный износ в процентах
        """
        if element_type in self.wear_limits and construction_type in self.wear_limits[element_type]:
            return self.wear_limits[element_type][construction_type]
        else:
            # Если тип не найден, возвращаем значение по умолчанию
            return 70.0  # Значение по умолчанию

    def get_repair_type(self, current_wear: float) -> str:
        """
        Определить тип ремонта на основе текущего износа.

        :param current_wear: Текущий износ в процентах
        :return: Тип ремонта ('routine_maintenance', 'minor_repair', 'major_repair', 'reconstruction')
        """
        for repair_type, (min_wear, max_wear) in self.repair_types.items():
            if min_wear <= current_wear < max_wear:
                return repair_type
        
        # Если износ превышает 100%, возвращаем реконструкцию
        return 'reconstruction'

    def is_repair_needed(self, element_type: str, construction_type: str, current_wear: float) -> bool:
        """
        Определить необходимость проведения ремонтных работ.

        :param element_type: Тип элемента
        :param construction_type: Тип конструкции
        :param current_wear: Текущий износ
        :return: True, если требуется ремонт, иначе False
        """
        limit = self.get_wear_limit(element_type, construction_type)
        return current_wear >= limit

    def get_repair_priority(self, element_type: str, construction_type: str, current_wear: float) -> int:
        """
        Определить приоритет выполнения ремонтных работ (от 1 до 5, где 5 - высший приоритет).

        :param element_type: Тип элемента
        :param construction_type: Тип конструкции
        :param current_wear: Текущий износ
        :return: Приоритет (целое число от 1 до 5)
        """
        limit = self.get_wear_limit(element_type, construction_type)
        
        # Вычисляем разницу между предельным и текущим износом
        difference = limit - current_wear
        
        # Определяем приоритет на основе разницы
        if difference <= 0:
            # Износ уже достиг или превысил предельный уровень
            return 5
        elif difference <= 5:
            # Износ близок к предельному уровню
            return 4
        elif difference <= 10:
            # Износ значительно выше нормы
            return 3
        elif difference <= 20:
            # Износ выше нормы, но не критично
            return 2
        else:
            # Износ в допустимых пределах
            return 1