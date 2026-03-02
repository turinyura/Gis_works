"""
Модуль оценки износа по ВСН 53-86р
Единые нормы предельных износов элементов жилых зданий
"""

from .calculator import VSN5386Calculator
from .rules import VSN5386Rules
from mkd_manager.models.building import Building
from mkd_manager.models.work import Work, WorkCategory
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class WearAssessment:
    """
    Класс для выполнения оценки износа здания по ВСН 53-86р и формирования
    рекомендаций по ремонтным работам на основе полученных данных.
    """
    
    def __init__(self):
        """
        Инициализирует оценку износа с использованием калькулятора и правил ВСН 53-86р
        """
        self.calculator = VSN5386Calculator()
        self.rules = VSN5386Rules()
    
    def assess_building_wear(self, building: Building) -> Dict:
        """
        Выполняет комплексную оценку износа здания
        
        :param building: Объект здания
        :return: Результаты оценки износа
        """
        # Подготовка данных элементов здания для расчета
        building_elements = self._prepare_building_elements(building)
        
        # Расчет комплексного износа
        comprehensive_assessment = self.calculator.calculate_building_comprehensive_wear(building_elements)
        
        # Расчет оценки стоимости ремонтов
        cost_assessment = self.calculator.calculate_repair_cost_estimate(building_elements)
        
        # Формирование рекомендаций по работам
        recommendations = self._generate_work_recommendations(comprehensive_assessment, building)
        
        return {
            'building_id': building.id,
            'address': building.address,
            'assessment_date': datetime.now().isoformat(),
            'comprehensive_assessment': comprehensive_assessment,
            'cost_assessment': cost_assessment,
            'recommendations': recommendations,
            'summary': self._generate_summary_report(comprehensive_assessment, cost_assessment)
        }
    
    def _prepare_building_elements(self, building: Building) -> Dict[str, Dict]:
        """
        Подготавливает данные элементов здания для расчета износа
        
        :param building: Объект здания
        :return: Словарь с данными элементов здания
        """
        current_year = datetime.now().year
        building_age = current_year - building.year_built
        
        elements = {}
        
        # Фундамент
        elements['foundation'] = {
            'type': 'foundation',
            'construction_type': self._determine_foundation_type(building),
            'age': building_age,
            'condition_factor': self._get_condition_factor(building.foundation_wear),
            'maintenance_factor': 1.0,  # Можно рассчитывать на основе истории обслуживания
            'area': building.total_area * 0.1,  # Условная площадь фундамента
            'weight': 1.5  # Высокий вес в общем износе
        }
        
        # Стены
        elements['walls'] = {
            'type': 'walls',
            'construction_type': self._determine_wall_type(building),
            'age': building_age,
            'condition_factor': self._get_condition_factor(building.walls_wear),
            'maintenance_factor': 1.0,
            'area': building.total_area * 0.7,  # Условная площадь стен
            'weight': 1.2
        }
        
        # Перекрытия
        elements['floors'] = {
            'type': 'floors',
            'construction_type': self._determine_floor_type(building),
            'age': building_age,
            'condition_factor': self._get_condition_factor(building.foundation_wear),  # Используем общий показатель
            'maintenance_factor': 1.0,
            'area': building.total_area,
            'weight': 1.0
        }
        
        # Кровля
        elements['roof'] = {
            'type': 'roof',
            'construction_type': self._determine_roof_type(building),
            'age': building_age,
            'condition_factor': self._get_condition_factor(building.roof_wear),
            'maintenance_factor': 1.0,
            'area': building.total_area,
            'weight': 0.8
        }
        
        # Инженерные системы
        elements['engineering_systems'] = {
            'type': 'engineering_systems',
            'construction_type': 'combined',
            'age': building_age,
            'condition_factor': self._get_condition_factor(building.engineering_wear),
            'maintenance_factor': 1.0,
            'area': building.total_area,
            'weight': 1.0
        }
        
        return elements
    
    def _determine_foundation_type(self, building: Building) -> str:
        """Определяет тип фундамента здания"""
        # В реальной системе тип фундамента должен быть в модели здания
        # Здесь используем эвристику на основе года постройки
        if building.year_built < 1960:
            return 'stone_concrete'
        elif building.year_built < 1990:
            return 'precast_concrete'
        else:
            return 'concrete'
    
    def _determine_wall_type(self, building: Building) -> str:
        """Определяет тип стен здания"""
        # Эвристическая оценка типа стен
        if building.year_built < 1960:
            return 'stone_brick'
        elif building.year_built < 1990:
            return 'large_block'
        else:
            return 'large_panel'
    
    def _determine_floor_type(self, building: Building) -> str:
        """Определяет тип перекрытий здания"""
        if building.year_built < 1960:
            return 'wooden'
        else:
            return 'concrete'
    
    def _determine_roof_type(self, building: Building) -> str:
        """Определяет тип кровли здания"""
        if building.year_built < 1960:
            return 'tile_roof'
        elif building.year_built < 1990:
            return 'soft_roof'
        else:
            return 'metal_roof'
    
    def _get_condition_factor(self, wear_percentage: float) -> float:
        """
        Преобразует процент износа в коэффициент состояния
        
        :param wear_percentage: Процент износа
        :return: Коэффициент состояния (чем больше износ, тем меньше коэффициент)
        """
        # Чем выше износ, тем хуже состояние
        # 0% износа -> 1.5 (отличное состояние)
        # 100% износа -> 0.5 (плохое состояние)
        factor = 1.5 - (wear_percentage / 100.0) * 1.0
        return max(0.5, min(1.5, factor))
    
    def _generate_work_recommendations(
        self, 
        assessment: Dict, 
        building: Building
    ) -> List[Dict]:
        """
        Генерирует рекомендации по ремонтным работам на основе оценки
        
        :param assessment: Результаты оценки износа
        :param building: Объект здания
        :return: Список рекомендованных работ
        """
        recommendations = []
        
        for element_name, element_result in assessment['elements_results'].items():
            if element_result['repair_needed']:
                # Определяем тип требуемых работ на основе типа элемента и типа ремонта
                work_type = self._map_element_and_repair_to_work(element_name, element_result['repair_type'])
                
                if work_type:
                    recommendation = {
                        'element': element_name,
                        'element_type': element_result['element_type'],
                        'current_wear': element_result['current_wear'],
                        'recommended_work': work_type,
                        'priority': element_result['repair_priority'],
                        'estimated_cost': self._estimate_work_cost(element_name, element_result, building),
                        'urgency_level': self._determine_urgency_level(element_result['repair_priority']),
                        'implementation_period': self._determine_implementation_period(element_result['repair_type'])
                    }
                    
                    recommendations.append(recommendation)
        
        # Сортируем рекомендации по приоритету
        recommendations.sort(key=lambda x: x['priority'], reverse=True)
        
        return recommendations
    
    def _map_element_and_repair_to_work(self, element: str, repair_type: str) -> Optional[str]:
        """
        Сопоставляет элемент и тип ремонта с конкретной работой
        
        :param element: Название элемента
        :param repair_type: Тип ремонта
        :return: Описание рекомендованной работы
        """
        mapping = {
            ('foundation', 'major_repair'): 'Капитальный ремонт фундамента',
            ('foundation', 'reconstruction'): 'Замена или усиление фундамента',
            ('walls', 'major_repair'): 'Капитальный ремонт наружных стен',
            ('walls', 'reconstruction'): 'Восстановление конструкции стен',
            ('floors', 'major_repair'): 'Капитальный ремонт перекрытий',
            ('roof', 'major_repair'): 'Капитальный ремонт кровли',
            ('roof', 'routine_maintenance'): 'Текущий ремонт кровли',
            ('engineering_systems', 'major_repair'): 'Капитальный ремонт инженерных систем',
            ('engineering_systems', 'minor_repair'): 'Текущий ремонт инженерных систем'
        }
        
        return mapping.get((element, repair_type))
    
    def _estimate_work_cost(self, element: str, element_result: Dict, building: Building) -> float:
        """
        Оценивает стоимость работ для конкретного элемента
        
        :param element: Название элемента
        :param element_result: Результаты оценки элемента
        :param building: Объект здания
        :return: Оценочная стоимость работ
        """
        # Базовая стоимость на квадратный метр для разных типов работ
        cost_per_sqm = {
            'foundation': 15000,
            'walls': 8000,
            'floors': 12000,
            'roof': 10000,
            'engineering_systems': 5000
        }
        
        # Определяем площадь или объем работ
        if element == 'foundation':
            area = building.total_area * 0.1
        elif element == 'walls':
            area = building.total_area * 0.7
        elif element in ['floors', 'roof', 'engineering_systems']:
            area = building.total_area
        else:
            area = building.total_area * 0.5
        
        base_cost = area * cost_per_sqm.get(element_result['element_type'], 10000)
        
        # Учитываем степень износа для увеличения стоимости
        wear_factor = element_result['current_wear'] / 100.0
        final_cost = base_cost * (1 + wear_factor * 0.5)  # Дополнительная стоимость пропорционально износу
        
        return round(final_cost, 2)
    
    def _determine_urgency_level(self, priority: int) -> str:
        """
        Определяет уровень срочности выполнения работ
        
        :param priority: Приоритет (1-5)
        :return: Описание уровня срочности
        """
        if priority >= 5:
            return "Неотложный"
        elif priority >= 4:
            return "Высокий"
        elif priority >= 3:
            return "Средний"
        elif priority >= 2:
            return "Низкий"
        else:
            return "Плановый"
    
    def _determine_implementation_period(self, repair_type: str) -> str:
        """
        Определяет период реализации работ
        
        :param repair_type: Тип ремонта
        :return: Период реализации
        """
        periods = {
            'routine_maintenance': 'Текущий год',
            'minor_repair': '1-2 года',
            'major_repair': '2-3 года',
            'reconstruction': '3-5 лет'
        }
        
        return periods.get(repair_type, 'По мере необходимости')
    
    def _generate_summary_report(self, comprehensive_assessment: Dict, cost_assessment: Dict) -> Dict:
        """
        Генерирует сводный отчет по оценке износа
        
        :param comprehensive_assessment: Комплексная оценка
        :param cost_assessment: Оценка стоимости
        :return: Сводный отчет
        """
        return {
            'overall_wear': comprehensive_assessment['overall_wear'],
            'wear_category': comprehensive_assessment['wear_category'],
            'total_elements': comprehensive_assessment['total_elements'],
            'elements_needing_repair': comprehensive_assessment['elements_needing_repair'],
            'estimated_total_cost': cost_assessment['total_estimated_cost'],
            'currency': cost_assessment['currency'],
            'recommendations_count': len(comprehensive_assessment['elements_results']),
            'highest_priority_items': self._get_highest_priority_items(comprehensive_assessment)
        }
    
    def _get_highest_priority_items(self, assessment: Dict) -> List[str]:
        """
        Получает список элементов с наивысшим приоритетом
        
        :param assessment: Результаты оценки
        :return: Список элементов с высоким приоритетом
        """
        high_priority = []
        
        for element_name, result in assessment['elements_results'].items():
            if result['repair_priority'] >= 4:  # Высокий или критический приоритет
                high_priority.append({
                    'element': element_name,
                    'wear': result['current_wear'],
                    'priority': result['repair_priority']
                })
        
        # Сортируем по износу (сначала самые изношенные)
        high_priority.sort(key=lambda x: x['wear'], reverse=True)
        
        return high_priority