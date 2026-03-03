import sys
import os
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QTextBrowser, QTreeWidget, QTreeWidgetItem, QFileDialog,
    QLabel, QHBoxLayout, QSplitter
)
from PyQt6.QtCore import Qt


class WorkDescriptionParser:
    """Класс для парсинга описания работ из Markdown"""
    
    def __init__(self):
        self.connection = None
        
    def connect_to_db(self, db_path="work_database.db"):
        """Подключение к базе данных"""
        self.connection = sqlite3.connect(db_path)
        self.create_tables()
        
    def create_tables(self):
        """Создание таблиц в базе данных если они не существуют"""
        cursor = self.connection.cursor()
        
        # Основная таблица описаний работ
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_number TEXT UNIQUE,
                title TEXT,
                description TEXT,
                purpose TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица юридических документов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS legal_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id INTEGER,
                document_name TEXT,
                article_section TEXT,
                FOREIGN KEY (work_id) REFERENCES work_descriptions (id)
            )
        """)
        
        # Таблица целей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_objectives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id INTEGER,
                objective TEXT,
                FOREIGN KEY (work_id) REFERENCES work_descriptions (id)
            )
        """)
        
        # Таблица типов запросов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS request_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id INTEGER,
                category TEXT,
                examples TEXT,
                priority_level TEXT,
                response_time TEXT,
                FOREIGN KEY (work_id) REFERENCES work_descriptions (id)
            )
        """)
        
        # Таблица этапов выполнения
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_stages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id INTEGER,
                stage_number INTEGER,
                stage_name TEXT,
                duration_limit TEXT,
                description TEXT,
                FOREIGN KEY (work_id) REFERENCES work_descriptions (id)
            )
        """)
        
        # Таблица инструментов и оборудования
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tools_equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id INTEGER,
                item_name TEXT,
                purpose TEXT,
                requirements TEXT,
                FOREIGN KEY (work_id) REFERENCES work_descriptions (id)
            )
        """)
        
        # Таблица параметров качества
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id INTEGER,
                parameter_name TEXT,
                normative_value TEXT,
                critical_value TEXT,
                regulation_reference TEXT,
                FOREIGN KEY (work_id) REFERENCES work_descriptions (id)
            )
        """)
        
        # Таблица KPI
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kpi_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id INTEGER,
                kpi_name TEXT,
                target_value TEXT,
                calculation_method TEXT,
                FOREIGN KEY (work_id) REFERENCES work_descriptions (id)
            )
        """)
        
        # Таблица обязанностей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS responsibilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id INTEGER,
                position TEXT,
                duties TEXT,
                FOREIGN KEY (work_id) REFERENCES work_descriptions (id)
            )
        """)
        
        # Таблица связанных работ
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS related_works (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id INTEGER,
                related_work_number TEXT,
                relationship_type TEXT,
                FOREIGN KEY (work_id) REFERENCES work_descriptions (id)
            )
        """)
        
        self.connection.commit()
    
    def extract_work_data(self, md_content):
        """Извлечение данных из Markdown-контента"""
        # Конвертируем Markdown в HTML
        html_content = markdown.markdown(md_content)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Ищем заголовок (обычно это первый h1 или h2)
        title_elem = soup.find(['h1', 'h2'])
        title = title_elem.get_text().strip() if title_elem else "Без названия"
        
        # Ищем номер работы в тексте (например, №19)
        work_number = ""
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text()
            if "№" in text or "#" in text:
                import re
                match = re.search(r'[№#]\s*(\d+(?:-\d+)?)', text)
                if match:
                    work_number = match.group(1)
                    break
        
        # Если не нашли номер в параграфах, пробуем найти в заголовке
        if not work_number:
            if "№" in title or "#" in title:
                import re
                match = re.search(r'[№#]\s*(\d+(?:-\d+)?)', title)
                if match:
                    work_number = match.group(1)
                    # Удаляем номер из заголовка
                    title = re.sub(r'[№#]\s*\d+(?:-\d+)?', '', title).strip()
        
        # Описание - весь текст кроме заголовков
        description_parts = []
        for elem in soup.find_all(['p', 'li']):
            text = elem.get_text().strip()
            if text and text != title:
                description_parts.append(text)
        description = "\n".join(description_parts[:10])  # Берем первые 10 частей
        
        # Цели (обычно после заголовка "Цели:" или "Цель:")
        objectives = []
        for heading in soup.find_all(['h2', 'h3']):
            if any(word in heading.get_text().lower() for word in ['цель', 'цели', 'objectives']):
                next_elem = heading.find_next_sibling()
                if next_elem:
                    if next_elem.name == 'ul':
                        objectives.extend([li.get_text().strip() for li in next_elem.find_all('li')])
                    elif next_elem.name == 'p':
                        objectives.append(next_elem.get_text().strip())
        
        # Правовые документы (обычно после заголовка "Правовая база:" или "Нормативные документы:")
        legal_docs = []
        for heading in soup.find_all(['h2', 'h3']):
            if any(word in heading.get_text().lower() for word in ['правовая', 'нормативные', 'документы', 'regulations']):
                next_elem = heading.find_next_sibling()
                if next_elem:
                    if next_elem.name == 'ul':
                        legal_docs.extend([li.get_text().strip() for li in next_elem.find_all('li')])
                    elif next_elem.name == 'p':
                        legal_docs.append(next_elem.get_text().strip())
        
        # Типы запросов (обычно после заголовка "Типы запросов:" или "Категории:")
        request_types = []
        for heading in soup.find_all(['h2', 'h3']):
            if any(word in heading.get_text().lower() for word in ['запросы', 'категории', 'types']):
                next_elem = heading.find_next_sibling()
                if next_elem and next_elem.name == 'ul':
                    for li in next_elem.find_all('li'):
                        text = li.get_text().strip()
                        # Пытаемся разделить на категории и примеры
                        parts = text.split(':')
                        if len(parts) >= 2:
                            category = parts[0].strip()
                            examples = ':'.join(parts[1:]).strip()
                            request_types.append({
                                'category': category,
                                'examples': examples
                            })
        
        # Этапы выполнения (обычно после заголовка "Этапы:" или "Процесс:")
        work_stages = []
        for heading in soup.find_all(['h2', 'h3']):
            if any(word in heading.get_text().lower() for word in ['этапы', 'процесс', 'steps']):
                next_elem = heading.find_next_sibling()
                if next_elem and next_elem.name == 'ol':
                    for i, li in enumerate(next_elem.find_all('li'), 1):
                        text = li.get_text().strip()
                        work_stages.append({
                            'stage_number': i,
                            'stage_name': f"Этап {i}",
                            'description': text
                        })
                elif next_elem and next_elem.name == 'ul':
                    for i, li in enumerate(next_elem.find_all('li'), 1):
                        text = li.get_text().strip()
                        work_stages.append({
                            'stage_number': i,
                            'stage_name': f"Этап {i}",
                            'description': text
                        })
        
        # Инструменты и оборудование (обычно после заголовка "Оборудование:" или "Инструменты:")
        tools_equipment = []
        for heading in soup.find_all(['h2', 'h3']):
            if any(word in heading.get_text().lower() for word in ['оборудование', 'инструменты', 'equipment', 'tools']):
                next_elem = heading.find_next_sibling()
                if next_elem and next_elem.name == 'ul':
                    for li in next_elem.find_all('li'):
                        text = li.get_text().strip()
                        tools_equipment.append({
                            'item_name': text,
                            'purpose': '',
                            'requirements': ''
                        })
        
        # Параметры качества (обычно после заголовка "Параметры качества:" или "Метрики:")
        quality_params = []
        for heading in soup.find_all(['h2', 'h3']):
            if any(word in heading.get_text().lower() for word in ['параметры', 'метрики', 'качество', 'metrics', 'quality']):
                next_elem = heading.find_next_sibling()
                if next_elem and next_elem.name == 'ul':
                    for li in next_elem.find_all('li'):
                        text = li.get_text().strip()
                        quality_params.append({
                            'parameter_name': text,
                            'normative_value': '',
                            'critical_value': '',
                            'regulation_reference': ''
                        })
        
        # KPI (обычно после заголовка "KPI:" или "Показатели:")
        kpi_metrics = []
        for heading in soup.find_all(['h2', 'h3']):
            if any(word in heading.get_text().lower() for word in ['kpi', 'показатели', 'индикаторы']):
                next_elem = heading.find_next_sibling()
                if next_elem and next_elem.name == 'ul':
                    for li in next_elem.find_all('li'):
                        text = li.get_text().strip()
                        kpi_metrics.append({
                            'kpi_name': text,
                            'target_value': '',
                            'calculation_method': ''
                        })
        
        # Обязанности (обычно после заголовка "Обязанности:" или "Функции:")
        responsibilities = []
        for heading in soup.find_all(['h2', 'h3']):
            if any(word in heading.get_text().lower() for word in ['обязанности', 'функции', 'roles', 'responsibilities']):
                next_elem = heading.find_next_sibling()
                if next_elem and next_elem.name == 'ul':
                    for li in next_elem.find_all('li'):
                        text = li.get_text().strip()
                        responsibilities.append({
                            'position': 'Должность не указана',
                            'duties': text
                        })
        
        # Связанные работы (обычно после заголовка "Связанные работы:" или "Отношения:")
        related_works = []
        for heading in soup.find_all(['h2', 'h3']):
            if any(word in heading.get_text().lower() for word in ['связанные', 'отношения', 'related']):
                next_elem = heading.find_next_sibling()
                if next_elem and next_elem.name == 'ul':
                    for li in next_elem.find_all('li'):
                        text = li.get_text().strip()
                        related_works.append({
                            'related_work_number': 'Не указан',
                            'relationship_type': text
                        })
        
        return {
            'title': title,
            'work_number': work_number,
            'description': description,
            'objectives': objectives,
            'legal_documents': legal_docs,
            'request_types': request_types,
            'work_stages': work_stages,
            'tools_equipment': tools_equipment,
            'quality_parameters': quality_params,
            'kpi_metrics': kpi_metrics,
            'responsibilities': responsibilities,
            'related_works': related_works
        }
    
    def save_work_to_db(self, work_data):
        """Сохранение данных о работе в базу данных"""
        if not self.connection:
            raise Exception("Нет подключения к базе данных")
        
        cursor = self.connection.cursor()
        
        # Проверяем, существует ли уже работа с таким номером
        cursor.execute("SELECT id FROM work_descriptions WHERE work_number = ?", (work_data['work_number'],))
        existing = cursor.fetchone()
        
        if existing:
            work_id = existing[0]
            # Обновляем существующую запись
            cursor.execute("""
                UPDATE work_descriptions 
                SET title = ?, description = ?, purpose = ?
                WHERE work_number = ?
            """, (
                work_data['title'],
                work_data['description'],
                f"Описание работы №{work_data['work_number']}",
                work_data['work_number']
            ))
        else:
            # Создаем новую запись
            cursor.execute("""
                INSERT INTO work_descriptions (work_number, title, description, purpose)
                VALUES (?, ?, ?, ?)
            """, (
                work_data['work_number'],
                work_data['title'],
                work_data['description'],
                f"Описание работы №{work_data['work_number']}"
            ))
            work_id = cursor.lastrowid
        
        # Сохраняем цели
        cursor.execute("DELETE FROM work_objectives WHERE work_id = ?", (work_id,))
        for obj in work_data['objectives']:
            cursor.execute("""
                INSERT INTO work_objectives (work_id, objective)
                VALUES (?, ?)
            """, (work_id, obj))
        
        # Сохраняем правовые документы
        cursor.execute("DELETE FROM legal_documents WHERE work_id = ?", (work_id,))
        for doc in work_data['legal_documents']:
            cursor.execute("""
                INSERT INTO legal_documents (work_id, document_name, article_section)
                VALUES (?, ?, ?)
            """, (work_id, doc, ""))
        
        # Сохраняем типы запросов
        cursor.execute("DELETE FROM request_types WHERE work_id = ?", (work_id,))
        for req_type in work_data['request_types']:
            cursor.execute("""
                INSERT INTO request_types (work_id, category, examples, priority_level, response_time)
                VALUES (?, ?, ?, ?, ?)
            """, (
                work_id,
                req_type.get('category', ''),
                req_type.get('examples', ''),
                req_type.get('priority_level', ''),
                req_type.get('response_time', '')
            ))
        
        # Сохраняем этапы выполнения
        cursor.execute("DELETE FROM work_stages WHERE work_id = ?", (work_id,))
        for stage in work_data['work_stages']:
            cursor.execute("""
                INSERT INTO work_stages (work_id, stage_number, stage_name, duration_limit, description)
                VALUES (?, ?, ?, ?, ?)
            """, (
                work_id,
                stage.get('stage_number', 0),
                stage.get('stage_name', ''),
                stage.get('duration_limit', ''),
                stage.get('description', '')
            ))
        
        # Сохраняем инструменты и оборудование
        cursor.execute("DELETE FROM tools_equipment WHERE work_id = ?", (work_id,))
        for tool in work_data['tools_equipment']:
            cursor.execute("""
                INSERT INTO tools_equipment (work_id, item_name, purpose, requirements)
                VALUES (?, ?, ?, ?)
            """, (
                work_id,
                tool.get('item_name', ''),
                tool.get('purpose', ''),
                tool.get('requirements', '')
            ))
        
        # Сохраняем параметры качества
        cursor.execute("DELETE FROM quality_parameters WHERE work_id = ?", (work_id,))
        for param in work_data['quality_parameters']:
            cursor.execute("""
                INSERT INTO quality_parameters (work_id, parameter_name, normative_value, critical_value, regulation_reference)
                VALUES (?, ?, ?, ?, ?)
            """, (
                work_id,
                param.get('parameter_name', ''),
                param.get('normative_value', ''),
                param.get('critical_value', ''),
                param.get('regulation_reference', '')
            ))
        
        # Сохраняем KPI
        cursor.execute("DELETE FROM kpi_metrics WHERE work_id = ?", (work_id,))
        for kpi in work_data['kpi_metrics']:
            cursor.execute("""
                INSERT INTO kpi_metrics (work_id, kpi_name, target_value, calculation_method)
                VALUES (?, ?, ?, ?)
            """, (
                work_id,
                kpi.get('kpi_name', ''),
                kpi.get('target_value', ''),
                kpi.get('calculation_method', '')
            ))
        
        # Сохраняем обязанности
        cursor.execute("DELETE FROM responsibilities WHERE work_id = ?", (work_id,))
        for resp in work_data['responsibilities']:
            cursor.execute("""
                INSERT INTO responsibilities (work_id, position, duties)
                VALUES (?, ?, ?)
            """, (
                work_id,
                resp.get('position', ''),
                resp.get('duties', '')
            ))
        
        # Сохраняем связанные работы
        cursor.execute("DELETE FROM related_works WHERE work_id = ?", (work_id,))
        for rel_work in work_data['related_works']:
            cursor.execute("""
                INSERT INTO related_works (work_id, related_work_number, relationship_type)
                VALUES (?, ?, ?)
            """, (
                work_id,
                rel_work.get('related_work_number', ''),
                rel_work.get('relationship_type', '')
            ))
        
        self.connection.commit()
        return work_id
    
    def load_md_files_from_directory(self, directory_path):
        """Загрузка и обработка всех файлов .md из директории"""
        md_files = list(Path(directory_path).glob("*.md"))
        processed_count = 0
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                work_data = self.extract_work_data(content)
                
                # Проверяем, что у нас есть минимальные данные для сохранения
                if work_data['work_number'] or work_data['title'] != "Без названия":
                    self.save_work_to_db(work_data)
                    processed_count += 1
            except Exception as e:
                print(f"Ошибка обработки файла {md_file}: {e}")
        
        return processed_count


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система управления описаниями работ")
        self.setGeometry(100, 100, 1200, 800)
        
        self.parser = WorkDescriptionParser()
        self.parser.connect_to_db()
        
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Кнопка загрузки работ
        self.load_button = QPushButton("Загрузить работы")
        self.load_button.clicked.connect(self.load_works)
        layout.addWidget(self.load_button)
        
        # Разделитель
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Список работ слева
        self.works_list = QTreeWidget()
        self.works_list.setHeaderLabel("Список работ")
        self.works_list.itemClicked.connect(self.show_work_details)
        splitter.addWidget(self.works_list)
        
        # Детали работы справа
        self.details_browser = QTextBrowser()
        splitter.addWidget(self.details_browser)
        
        splitter.setSizes([300, 900])
        
        # Загружаем список работ
        self.refresh_works_list()
    
    def load_works(self):
        """Загрузка работ из выбранной папки"""
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку с файлами описаний работ")
        
        if directory:
            try:
                count = self.parser.load_md_files_from_directory(directory)
                self.statusBar().showMessage(f"Обработано {count} файлов", 3000)
                self.refresh_works_list()
            except Exception as e:
                self.statusBar().showMessage(f"Ошибка: {str(e)}", 5000)
    
    def refresh_works_list(self):
        """Обновление списка работ"""
        self.works_list.clear()
        
        cursor = self.parser.connection.cursor()
        cursor.execute("SELECT id, work_number, title FROM work_descriptions ORDER BY work_number")
        works = cursor.fetchall()
        
        for work_id, work_number, title in works:
            item = QTreeWidgetItem(self.works_list, [f"№{work_number}", title])
            item.setData(0, Qt.ItemDataRole.UserRole, work_id)
    
    def show_work_details(self, item):
        """Отображение деталей выбранной работы"""
        work_id = item.data(0, Qt.ItemDataRole.UserRole)
        
        if not work_id:
            return
        
        cursor = self.parser.connection.cursor()
        
        # Получаем основную информацию о работе
        cursor.execute("""
            SELECT work_number, title, description, purpose 
            FROM work_descriptions 
            WHERE id = ?
        """, (work_id,))
        work_info = cursor.fetchone()
        
        if not work_info:
            return
        
        work_number, title, description, purpose = work_info
        
        # Формируем HTML для отображения
        html_content = f"""
        <h2>Работа №{work_number} - {title}</h2>
        <p><strong>Назначение:</strong> {purpose}</p>
        <p><strong>Описание:</strong></p>
        <p>{description}</p>
        """
        
        # Добавляем цели
        cursor.execute("SELECT objective FROM work_objectives WHERE work_id = ?", (work_id,))
        objectives = cursor.fetchall()
        if objectives:
            html_content += "<h3>Цели:</h3><ul>"
            for obj in objectives:
                html_content += f"<li>{obj[0]}</li>"
            html_content += "</ul>"
        
        # Добавляем правовые документы
        cursor.execute("SELECT document_name, article_section FROM legal_documents WHERE work_id = ?", (work_id,))
        legal_docs = cursor.fetchall()
        if legal_docs:
            html_content += "<h3>Правовая база:</h3><ul>"
            for doc, section in legal_docs:
                if section:
                    html_content += f"<li>{doc} - {section}</li>"
                else:
                    html_content += f"<li>{doc}</li>"
            html_content += "</ul>"
        
        # Добавляем типы запросов
        cursor.execute("SELECT category, examples, priority_level, response_time FROM request_types WHERE work_id = ?", (work_id,))
        request_types = cursor.fetchall()
        if request_types:
            html_content += "<h3>Типы запросов:</h3><ul>"
            for category, examples, priority, response_time in request_types:
                html_content += f"<li><strong>{category}</strong>: {examples}"
                if priority:
                    html_content += f" (Приоритет: {priority})"
                if response_time:
                    html_content += f" (Время реакции: {response_time})"
                html_content += "</li>"
            html_content += "</ul>"
        
        # Добавляем этапы выполнения
        cursor.execute("SELECT stage_number, stage_name, duration_limit, description FROM work_stages WHERE work_id = ? ORDER BY stage_number", (work_id,))
        stages = cursor.fetchall()
        if stages:
            html_content += "<h3>Этапы выполнения:</h3><ol>"
            for num, name, duration, desc in stages:
                html_content += f"<li><strong>{name}</strong>"
                if duration:
                    html_content += f" (Срок: {duration})"
                if desc:
                    html_content += f"<br>{desc}"
                html_content += "</li>"
            html_content += "</ol>"
        
        # Добавляем инструменты и оборудование
        cursor.execute("SELECT item_name, purpose, requirements FROM tools_equipment WHERE work_id = ?", (work_id,))
        tools = cursor.fetchall()
        if tools:
            html_content += "<h3>Инструменты и оборудование:</h3><ul>"
            for name, purpose, reqs in tools:
                html_content += f"<li><strong>{name}</strong>"
                if purpose:
                    html_content += f" - {purpose}"
                if reqs:
                    html_content += f" (Требования: {reqs})"
                html_content += "</li>"
            html_content += "</ul>"
        
        # Добавляем параметры качества
        cursor.execute("SELECT parameter_name, normative_value, critical_value, regulation_reference FROM quality_parameters WHERE work_id = ?", (work_id,))
        params = cursor.fetchall()
        if params:
            html_content += "<h3>Параметры качества:</h3><ul>"
            for name, norm, crit, ref in params:
                html_content += f"<li><strong>{name}</strong>"
                if norm:
                    html_content += f" (Норматив: {norm})"
                if crit:
                    html_content += f" (Критический: {crit})"
                if ref:
                    html_content += f" (Нормативный документ: {ref})"
                html_content += "</li>"
            html_content += "</ul>"
        
        # Добавляем KPI
        cursor.execute("SELECT kpi_name, target_value, calculation_method FROM kpi_metrics WHERE work_id = ?", (work_id,))
        kpis = cursor.fetchall()
        if kpis:
            html_content += "<h3>KPI:</h3><ul>"
            for name, target, method in kpis:
                html_content += f"<li><strong>{name}</strong>"
                if target:
                    html_content += f" (Целевое значение: {target})"
                if method:
                    html_content += f" (Метод расчета: {method})"
                html_content += "</li>"
            html_content += "</ul>"
        
        # Добавляем обязанности
        cursor.execute("SELECT position, duties FROM responsibilities WHERE work_id = ?", (work_id,))
        responsibilities = cursor.fetchall()
        if responsibilities:
            html_content += "<h3>Обязанности:</h3><ul>"
            for pos, duties in responsibilities:
                html_content += f"<li><strong>{pos}</strong>: {duties}</li>"
            html_content += "</ul>"
        
        # Добавляем связанные работы
        cursor.execute("SELECT related_work_number, relationship_type FROM related_works WHERE work_id = ?", (work_id,))
        related = cursor.fetchall()
        if related:
            html_content += "<h3>Связанные работы:</h3><ul>"
            for num, rel_type in related:
                html_content += f"<li>Работа №{num}: {rel_type}</li>"
            html_content += "</ul>"
        
        self.details_browser.setHtml(html_content)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()