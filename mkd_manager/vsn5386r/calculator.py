"""
Калькулятор износа по ВСН 53-86р
Единые нормы предельных износов элементов жилых зданий
"""

from .rules import VSN5386Rules
from typing import Dict, Any


class VSN5386Calculator:
    """
    Калькулятор износа по ВСН 53-86р
    Реализует методы расчета износа элементов здания по единым нормам предельных износов
    """
    
    def __init__(self):
        """
        Инициализирует калькулятор с правилами ВСН 53-86р
        """
        self.rules = VSN5386Rules()
    
    def calculate_element_wear(
        self,
        element_type: str,
        construction_type: str,
        age: int,
        condition_factor: float = 1.0,
        maintenance_factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Рассчитывает текущий износ элемента здания
        
        :param element_type: Тип элемента (foundation, walls, floors, roof, facade, engineering_systems)
        :param construction_type: Тип конструкции (stone_concrete, wooden, concrete и т.д.)
        :param age: Возраст элемента в годах
        :param condition_factor: Коэффициент состояния (0.5 - плохое, 1.0 - нормальное, 1.5 - хорошее)
        :param maintenance_factor: Коэффициент обслуживания (0.5 - плохо обслуживается, 1.0 - нормально, 1.5 - хорошо)
        :return: Словарь с результатами расчета
        """
        # Получаем предельный износ для данного типа элемента и конструкции
        max_wear = self.rules.get_wear_limit(element_type, construction_type)
        
        # Базовая формула расчета износа - линейная зависимость от возраста
        # Но с учетом коэффициентов состояния и обслуживания
        base_wear_rate = max_wear / 100  # базовая скорость износа в % за 100 лет эксплуатации
        years_to_max_wear = 100 / base_wear_rate if base_wear_rate > 0 else float('inf')
        
        # Рассчитываем износ с учетом коэффициентов
        adjusted_wear_rate = base_wear_rate * condition_factor * maintenance_factor
        current_wear = min(adjusted_wear_rate * age, 99.9)  # Не превышаем 100% для корректности
        
        # Определяем, требуется ли ремонт
        repair_needed = self.rules.is_repair_needed(element_type, construction_type, current_wear)
        
        # Определяем тип ремонта
        repair_type = self.rules.get_repair_type(current_wear)
        
        # Определяем приоритет ремонта
        repair_priority = self.rules.get_repair_priority(element_type, construction_type, current_wear)
        
        return {
            'element_type': element_type,
            'construction_type': construction_type,
            'current_wear': round(current_wear, 2),
            'max_wear': max_wear,
            'age': age,
            'condition_factor': condition_factor,
            'maintenance_factor': maintenance_factor,
            'repair_needed': repair_needed,
            'repair_type': repair_type,
            'repair_priority': repair_priority,
            'years_to_replacement': self._calculate_years_to_replacement(
                element_type, construction_type, current_wear, condition_factor, maintenance_factor
            )
        }
    
    def _calculate_years_to_replacement(
        self,
        element_type: str,
        construction_type: str,
        current_wear: float,
        condition_factor: float,
        maintenance_factor: float
    ) -> float:
        """
        Рассчитывает количество лет до достижения предельного износа
        
        :param element_type: Тип элемента
        :param construction_type: Тип конструкции
        :param current_wear: Текущий износ
        :param condition_factor: Коэффициент состояния
        :param maintenance_factor: Коэффициент обслуживания
        :return: Количество лет до замены
        """
        max_wear = self.rules.get_wear_limit(element_type, construction_type)
        remaining_wear = max_wear - current_wear
        
        if remaining_wear <= 0:
            return 0  # Уже требуется замена
        
        # Базовая скорость износа в год
        base_wear_rate = max_wear / 100  # % износа за год при 100-летнем сроке службы
        adjusted_wear_rate = base_wear_rate * condition_factor * maintenance_factor
        
        if adjusted_wear_rate <= 0:
            return float('inf')  # Не будет износа
        
        years_to_replacement = remaining_wear / adjusted_wear_rate
        return round(years_to_replacement, 2)
    
    def calculate_building_comprehensive_wear(
        self,
        building_elements: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Рассчитывает комплексный износ здания по всем элементам
        
        :param building_elements: Словарь элементов здания с их характеристиками
        :return: Результаты комплексного расчета износа
        """
        total_weighted_wear = 0
        total_weight = 0
        elements_results = {}
        
        for element_name, element_data in building_elements.items():
            element_result = self.calculate_element_wear(
                element_data['type'],
                element_data['construction_type'],
                element_data['age'],
                element_data.get('condition_factor', 1.0),
                element_data.get('maintenance_factor', 1.0)
            )
            
            # Весовой коэффициент для каждого элемента (влияние на общий износ)
            weight = element_data.get('weight', 1.0)
            
            total_weighted_wear += element_result['current_wear'] * weight
            total_weight += weight
            
            elements_results[element_name] = element_result
        
        # Средневзвешенный износ здания
        overall_wear = total_weighted_wear / total_weight if total_weight > 0 else 0
        
        # Определяем категорию износа здания
        if overall_wear < 20:
            wear_category = "I - Незначительный износ"
        elif overall_wear < 40:
            wear_category = "II - Слабый износ"
        elif overall_wear < 60:
            wear_category = "III - Средний износ"
        elif overall_wear < 75:
            wear_category = "IV - Сильный износ"
        else:
            wear_category = "V - Аварийный износ"
        
        return {
            'overall_wear': round(overall_wear, 2),
            'wear_category': wear_category,
            'elements_results': elements_results,
            'total_elements': len(elements_results),
            'elements_needing_repair': sum(1 for r in elements_results.values() if r['repair_needed'])
        }
    
    def calculate_repair_cost_estimate(
        self,
        building_elements: Dict[str, Dict[str, Any]],
        cost_per_unit: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Рассчитывает ориентировочную стоимость ремонтных работ
        
        :param building_elements: Словарь элементов здания
        :param cost_per_unit: Словарь стоимости ремонта за единицу измерения
        :return: Оценка стоимости ремонтных работ
        """
        if cost_per_unit is None:
            # Стандартные стоимости за единицу (условные значения)
            cost_per_unit = {
                'foundation': 15000,  # руб/м2
                'walls': 8000,        # руб/м2
                'floors': 12000,      # руб/м2
                'roof': 10000,        # руб/м2
                'facade': 7000,       # руб/м2
                'engineering_systems': 5000  # руб/м2
            }
        
        total_cost = 0
        repair_details = {}
        
        for element_name, element_data in building_elements.items():
            element_result = self.calculate_element_wear(
                element_data['type'],
                element_data['construction_type'],
                element_data['age'],
                element_data.get('condition_factor', 1.0),
                element_data.get('maintenance_factor', 1.0)
            )
            
            if element_result['repair_needed']:
                # Определяем объем работ (условно пропорционально износу)
                area = element_data.get('area', 100)  # условная площадь
                wear_percentage = element_result['current_wear'] / 100
                
                # Базовая стоимость ремонта
                base_cost = area * cost_per_unit.get(element_data['type'], 10000)
                
                # Увеличиваем стоимость в зависимости от степени износа
                repair_cost = base_cost * wear_percentage * element_data.get('cost_multiplier', 1.0)
                
                total_cost += repair_cost
                
                repair_details[element_name] = {
                    'cost': round(repair_cost, 2),
                    'area': area,
                    'wear_percentage': element_result['current_wear'],
                    'repair_type': element_result['repair_type']
                }
        
        return {
            'total_estimated_cost': round(total_cost, 2),
            'repair_details': repair_details,
            'currency': 'RUB',
            'valid_for_year': 2026  # год актуальности оценки
        }