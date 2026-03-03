"""
Главное окно приложения МКД-Менеджер
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QMenuBar, QStatusBar, QToolBar, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QMessageBox, QFileDialog, QDialog, QListWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QPixmap


class MainWindow(QMainWindow):
    """
    Главное окно приложения
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("МКД-Менеджер")
        self.setGeometry(100, 100, 1200, 800)
        
        # Применяем стили
        self.apply_styles()
        
        # Устанавливаем центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Создаем макет для центрального виджета
        layout = QVBoxLayout(self.central_widget)
    
    def apply_styles(self):
        """Применение стилей к интерфейсу"""
        try:
            with open('/workspace/mkd_manager/gui/styles.css', 'r', encoding='utf-8') as f:
                style_sheet = f.read()
            self.setStyleSheet(style_sheet)
        except FileNotFoundError:
            print("Файл стилей styles.css не найден")
        except Exception as e:
            print(f"Ошибка при загрузке стилей: {e}")
        
        # Создаем вкладки
        self.tab_widget = QTabWidget()
        
        # Вкладка "МКД"
        self.buildings_tab = self.create_buildings_tab()
        self.tab_widget.addTab(self.buildings_tab, "МКД")
        
        # Вкладка "Работы"
        self.works_tab = self.create_works_tab()
        self.tab_widget.addTab(self.works_tab, "Работы")
        
        # Вкладка "План работ"
        self.planning_tab = self.create_planning_tab()
        self.tab_widget.addTab(self.planning_tab, "План работ")
        
        # Вкладка "Отчеты"
        self.reports_tab = self.create_reports_tab()
        self.tab_widget.addTab(self.reports_tab, "Отчеты")
        
        layout.addWidget(self.tab_widget)
        
        # Создаем меню
        self.create_menu_bar()
        
        # Создаем панель инструментов
        self.create_tool_bar()
        
        # Создаем статусную строку
        self.create_status_bar()
        
    def create_menu_bar(self):
        """Создание строки меню"""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')
        
        new_action = QAction('Новый', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('Открыть', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('Сохранить', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Правка"
        edit_menu = menubar.addMenu('Правка')
        
        undo_action = QAction('Отменить', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('Повторить', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        # Меню "Вид"
        view_menu = menubar.addMenu('Вид')
        
        # Меню "Справка"
        help_menu = menubar.addMenu('Справка')
        
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.about_dialog)
        help_menu.addAction(about_action)
        
    def create_tool_bar(self):
        """Создание панели инструментов"""
        toolbar = self.addToolBar('Основная')
        
        # Добавляем кнопки на панель инструментов
        new_btn = QPushButton('Новый')
        new_btn.clicked.connect(self.new_file)
        toolbar.addWidget(new_btn)
        
        open_btn = QPushButton('Открыть')
        open_btn.clicked.connect(self.open_file)
        toolbar.addWidget(open_btn)
        
        save_btn = QPushButton('Сохранить')
        save_btn.clicked.connect(self.save_file)
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
        
        refresh_btn = QPushButton('Обновить')
        refresh_btn.clicked.connect(self.refresh_data)
        toolbar.addWidget(refresh_btn)
        
    def create_status_bar(self):
        """Создание статусной строки"""
        status_bar = self.statusBar()
        status_bar.showMessage('Готово')
        
    def create_buildings_tab(self):
        """Создание вкладки МКД"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Поиск
        search_layout = QHBoxLayout()
        search_label = QLabel('Поиск:')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Введите адрес или кадастровый номер...')
        search_button = QPushButton('Найти')
        search_button.clicked.connect(self.search_buildings)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)
        
        # Таблица МКД
        self.buildings_table = QTableWidget()
        self.buildings_table.setColumnCount(6)
        self.buildings_table.setHorizontalHeaderLabels([
            'Кадастровый номер', 'Адрес', 'Год постройки', 
            'Этажность', 'Лифты', 'Площадь'
        ])
        
        # Заполняем таблицу тестовыми данными
        self.populate_buildings_table()
        
        header = self.buildings_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.buildings_table)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        add_building_btn = QPushButton('Добавить МКД')
        add_building_btn.clicked.connect(self.add_building)
        edit_building_btn = QPushButton('Редактировать')
        edit_building_btn.clicked.connect(self.edit_building)
        delete_building_btn = QPushButton('Удалить')
        delete_building_btn.clicked.connect(self.delete_building)
        
        buttons_layout.addWidget(add_building_btn)
        buttons_layout.addWidget(edit_building_btn)
        buttons_layout.addWidget(delete_building_btn)
        layout.addLayout(buttons_layout)
        
        return tab
    
    def create_works_tab(self):
        """Создание вкладки Работы"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Список категорий работ
        categories_layout = QVBoxLayout()
        categories_label = QLabel('Категории работ:')
        self.categories_list = QListWidget()
        self.categories_list.addItems([
            'Содержание', 'Текущий ремонт', 'Управление', 
            'Диспетчеризация', 'Уборка территории',
            'Уборка МОП', 'Мусоропровод', 'Лифты',
            'Газовое хозяйство'
        ])
        self.categories_list.itemClicked.connect(self.filter_works_by_category)
        
        categories_layout.addWidget(categories_label)
        categories_layout.addWidget(self.categories_list)
        
        # Таблица работ
        works_layout = QVBoxLayout()
        works_label = QLabel('Работы:')
        self.works_table = QTableWidget()
        self.works_table.setColumnCount(5)
        self.works_table.setHorizontalHeaderLabels([
            'Код', 'Наименование', 'Категория', 'Периодичность', 'Ед. изм.'
        ])
        
        # Заполняем таблицу тестовыми данными
        self.populate_works_table()
        
        header = self.works_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        works_layout.addWidget(works_label)
        works_layout.addWidget(self.works_table)
        
        # Кнопки управления
        works_buttons_layout = QHBoxLayout()
        add_work_btn = QPushButton('Добавить работу')
        add_work_btn.clicked.connect(self.add_work)
        edit_work_btn = QPushButton('Редактировать')
        edit_work_btn.clicked.connect(self.edit_work)
        delete_work_btn = QPushButton('Удалить')
        delete_work_btn.clicked.connect(self.delete_work)
        
        works_buttons_layout.addWidget(add_work_btn)
        works_buttons_layout.addWidget(edit_work_btn)
        works_buttons_layout.addWidget(delete_work_btn)
        
        works_layout.addLayout(works_buttons_layout)
        
        # Компоновка
        layout.addLayout(categories_layout)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addLayout(works_layout)
        layout.addWidget(right_panel)
        
        return tab
    
    def create_planning_tab(self):
        """Создание вкладки План работ"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Информационная панель
        info_layout = QHBoxLayout()
        building_info_label = QLabel('Выбранный МКД: не выбран')
        period_info_label = QLabel('Период: 2024')
        info_layout.addWidget(building_info_label)
        info_layout.addStretch()
        info_layout.addWidget(period_info_label)
        layout.addLayout(info_layout)
        
        # Дерево работ
        self.planning_tree = QTreeWidget()
        self.planning_tree.setHeaderLabels([
            'Работа', 'Периодичность', 'Объем', 'Стоимость', 'Статус'
        ])
        
        # Добавляем тестовые данные
        self.populate_planning_tree()
        
        header = self.planning_tree.header()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.planning_tree)
        
        # Кнопки планирования
        planning_buttons_layout = QHBoxLayout()
        plan_btn = QPushButton('Запланировать')
        plan_btn.clicked.connect(self.plan_works)
        update_plan_btn = QPushButton('Обновить план')
        update_plan_btn.clicked.connect(self.update_plan)
        export_plan_btn = QPushButton('Экспорт плана')
        export_plan_btn.clicked.connect(self.export_plan)
        
        planning_buttons_layout.addWidget(plan_btn)
        planning_buttons_layout.addWidget(update_plan_btn)
        planning_buttons_layout.addWidget(export_plan_btn)
        layout.addLayout(planning_buttons_layout)
        
        return tab
    
    def create_reports_tab(self):
        """Создание вкладки Отчеты"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Выбор типа отчета
        report_type_layout = QHBoxLayout()
        report_type_label = QLabel('Тип отчета:')
        self.report_type_combo = QListWidget()
        self.report_type_combo.addItems([
            'Отчет по выполненным работам',
            'Отчет по затратам',
            'Отчет по состоянию МКД',
            'Отчет по графикам обслуживания',
            'Отчет по аварийным ситуациям'
        ])
        
        report_type_layout.addWidget(report_type_label)
        report_type_layout.addWidget(self.report_type_combo)
        
        layout.addLayout(report_type_layout)
        
        # Параметры отчета
        params_layout = QGridLayout()
        date_from_label = QLabel('Дата с:')
        self.date_from_input = QLineEdit()
        self.date_from_input.setText('01.01.2024')
        date_to_label = QLabel('Дата по:')
        self.date_to_input = QLineEdit()
        self.date_to_input.setText('31.12.2024')
        
        params_layout.addWidget(date_from_label, 0, 0)
        params_layout.addWidget(self.date_from_input, 0, 1)
        params_layout.addWidget(date_to_label, 0, 2)
        params_layout.addWidget(self.date_to_input, 0, 3)
        
        layout.addLayout(params_layout)
        
        # Область просмотра отчета
        self.report_view = QTextEdit()
        self.report_view.setReadOnly(True)
        layout.addWidget(self.report_view)
        
        # Кнопки генерации отчета
        report_buttons_layout = QHBoxLayout()
        generate_report_btn = QPushButton('Сформировать отчет')
        generate_report_btn.clicked.connect(self.generate_report)
        preview_report_btn = QPushButton('Предварительный просмотр')
        preview_report_btn.clicked.connect(self.preview_report)
        export_report_btn = QPushButton('Экспорт отчета')
        export_report_btn.clicked.connect(self.export_report)
        
        report_buttons_layout.addWidget(generate_report_btn)
        report_buttons_layout.addWidget(preview_report_btn)
        report_buttons_layout.addWidget(export_report_btn)
        layout.addLayout(report_buttons_layout)
        
        return tab
    
    def populate_buildings_table(self):
        """Заполнение таблицы МКД тестовыми данными"""
        self.buildings_table.setRowCount(5)
        
        # Пример данных
        buildings_data = [
            ['77:05:0001001:1000', 'г. Москва, ул. Тверская, д. 1', '1950', '9', '2', '3200'],
            ['77:05:0001002:2000', 'г. Москва, ул. Арбат, д. 10', '1965', '5', '1', '2100'],
            ['77:05:0001003:3000', 'г. Москва, ул. Новый Арбат, д. 21', '1980', '12', '4', '4500'],
            ['77:05:0001004:4000', 'г. Москва, ул. Охотный Ряд, д. 2', '1995', '16', '6', '6800'],
            ['77:05:0001005:5000', 'г. Москва, ул. Петровка, д. 35', '2005', '18', '8', '7200']
        ]
        
        for row_idx, row_data in enumerate(buildings_data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                self.buildings_table.setItem(row_idx, col_idx, item)
    
    def populate_works_table(self):
        """Заполнение таблицы работ тестовыми данными"""
        self.works_table.setRowCount(10)
        
        # Пример данных
        works_data = [
            ['1', 'Текущий ремонт фундамента', 'repair', 'по мере необходимости', 'м2'],
            ['2', 'Текущий ремонт несущих стен', 'repair', 'по мере необходимости', 'м2'],
            ['3', 'Текущий ремонт перегородок', 'repair', 'по мере необходимости', 'м2'],
            ['4', 'Текущий ремонт междуэтажных перекрытий', 'repair', 'по мере необходимости', 'м2'],
            ['5', 'Текущий ремонт чердачного перекрытия', 'repair', 'по мере необходимости', 'м2'],
            ['6', 'Текущий ремонт подвального перекрытия', 'repair', 'по мере необходимости', 'м2'],
            ['7', 'Текущий ремонт лестничных маршей и площадок', 'repair', 'по мере необходимости', 'м2'],
            ['8', 'Текущий ремонт оконных блоков', 'repair', 'по мере необходимости', 'шт'],
            ['9', 'Текущий ремонт дверных блоков', 'repair', 'по мере необходимости', 'шт'],
            ['10', 'Текущий ремонт кровли', 'repair', 'по мере необходимости', 'м2']
        ]
        
        for row_idx, row_data in enumerate(works_data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                self.works_table.setItem(row_idx, col_idx, item)
    
    def populate_planning_tree(self):
        """Заполнение дерева планирования тестовыми данными"""
        # Создаем узлы для разных категорий работ
        repair_item = QTreeWidgetItem(self.planning_tree, ['Текущий ремонт'])
        repair_item.setExpanded(True)
        
        repair_sub_items = [
            ['Фундамент', 'по мере необходимости', '320 м2', '1500000 руб.', 'Запланировано'],
            ['Несущие стены', 'по мере необходимости', '2100 м2', '8400000 руб.', 'Запланировано'],
            ['Перекрытия', 'по мере необходимости', '3200 м2', '6400000 руб.', 'Не запланировано']
        ]
        
        for sub_item_data in repair_sub_items:
            sub_item = QTreeWidgetItem(repair_item, sub_item_data)
        
        content_item = QTreeWidgetItem(self.planning_tree, ['Содержание'])
        content_item.setExpanded(True)
        
        content_sub_items = [
            ['Уборка МОП', 'ежедневно', '3200 м2', '1200000 руб.', 'Выполняется'],
            ['Вывоз ТКО', 'ежедневно', '12 т', '240000 руб.', 'Выполняется']
        ]
        
        for sub_item_data in content_sub_items:
            sub_item = QTreeWidgetItem(content_item, sub_item_data)
    
    # Методы для работы с МКД
    def search_buildings(self):
        """Поиск МКД"""
        search_text = self.search_input.text()
        QMessageBox.information(self, 'Поиск', f'Поиск по запросу: {search_text}')
    
    def add_building(self):
        """Добавление нового МКД"""
        QMessageBox.information(self, 'Добавить МКД', 'Функция добавления МКД')
    
    def edit_building(self):
        """Редактирование МКД"""
        selected_row = self.buildings_table.currentRow()
        if selected_row >= 0:
            cad_num = self.buildings_table.item(selected_row, 0).text()
            QMessageBox.information(self, 'Редактировать МКД', f'Редактирование МКД: {cad_num}')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Выберите МКД для редактирования')
    
    def delete_building(self):
        """Удаление МКД"""
        selected_row = self.buildings_table.currentRow()
        if selected_row >= 0:
            reply = QMessageBox.question(
                self, 'Подтверждение', 
                'Вы действительно хотите удалить выбранный МКД?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.buildings_table.removeRow(selected_row)
        else:
            QMessageBox.warning(self, 'Ошибка', 'Выберите МКД для удаления')
    
    # Методы для работы с работами
    def filter_works_by_category(self, item):
        """Фильтрация работ по категории"""
        category = item.text()
        QMessageBox.information(self, 'Фильтр', f'Фильтрация по категории: {category}')
    
    def add_work(self):
        """Добавление новой работы"""
        QMessageBox.information(self, 'Добавить работу', 'Функция добавления работы')
    
    def edit_work(self):
        """Редактирование работы"""
        selected_row = self.works_table.currentRow()
        if selected_row >= 0:
            work_code = self.works_table.item(selected_row, 0).text()
            QMessageBox.information(self, 'Редактировать работу', f'Редактирование работы: {work_code}')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Выберите работу для редактирования')
    
    def delete_work(self):
        """Удаление работы"""
        selected_row = self.works_table.currentRow()
        if selected_row >= 0:
            reply = QMessageBox.question(
                self, 'Подтверждение', 
                'Вы действительно хотите удалить выбранную работу?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.works_table.removeRow(selected_row)
        else:
            QMessageBox.warning(self, 'Ошибка', 'Выберите работу для удаления')
    
    # Методы для планирования
    def plan_works(self):
        """Планирование работ"""
        QMessageBox.information(self, 'Планирование', 'Функция планирования работ')
    
    def update_plan(self):
        """Обновление плана"""
        QMessageBox.information(self, 'Обновление плана', 'Функция обновления плана работ')
    
    def export_plan(self):
        """Экспорт плана"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Сохранить план', '', 'Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)'
        )
        if file_path:
            QMessageBox.information(self, 'Экспорт', f'План экспортирован в: {file_path}')
    
    # Методы для отчетов
    def generate_report(self):
        """Генерация отчета"""
        report_type = self.report_type_combo.currentItem()
        if report_type:
            self.report_view.setText(f'Сгенерирован отчет: {report_type.text()}\n\n'
                                   f'Период: {self.date_from_input.text()} - {self.date_to_input.text()}\n\n'
                                   'Данные отчета будут отображаться здесь...')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Выберите тип отчета')
    
    def preview_report(self):
        """Предварительный просмотр отчета"""
        QMessageBox.information(self, 'Просмотр', 'Функция предварительного просмотра отчета')
    
    def export_report(self):
        """Экспорт отчета"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Экспортировать отчет', '', 'PDF Files (*.pdf);;Excel Files (*.xlsx);;All Files (*)'
        )
        if file_path:
            QMessageBox.information(self, 'Экспорт', f'Отчет экспортирован в: {file_path}')
    
    # Общие методы
    def new_file(self):
        """Создать новый файл"""
        QMessageBox.information(self, 'Новый', 'Создание нового файла')
    
    def open_file(self):
        """Открыть файл"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Открыть файл', '', 'All Files (*)'
        )
        if file_path:
            QMessageBox.information(self, 'Открытие', f'Открыт файл: {file_path}')
    
    def save_file(self):
        """Сохранить файл"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Сохранить файл', '', 'All Files (*)'
        )
        if file_path:
            QMessageBox.information(self, 'Сохранение', f'Файл сохранен: {file_path}')
    
    def refresh_data(self):
        """Обновить данные"""
        QMessageBox.information(self, 'Обновление', 'Обновление данных')
    
    def undo(self):
        """Отменить действие"""
        pass
    
    def redo(self):
        """Повторить действие"""
        pass
    
    def about_dialog(self):
        """О программе"""
        QMessageBox.about(
            self, 
            'О программе', 
            'МКД-Менеджер\n\n'
            'Программа для автоматизации планирования, структурирования и контроля работ по содержанию и ремонту МКД\n\n'
            'Версия 1.0.0'
        )


def main():
    """Точка входа для GUI приложения"""
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()