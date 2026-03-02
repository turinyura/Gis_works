import networkx as nx
import matplotlib.pyplot as plt
from models.work import Work


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
                '#gray'
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