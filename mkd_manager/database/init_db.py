"""
Скрипт инициализации базы данных
"""

import json
import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import SQLModel, create_engine, Session
from models.work import Work, WorkCategory, WorkType
from config.settings import settings


def init_database():
    """Инициализация базы данных"""
    
    # Проверяем существование директории для базы данных
    db_dir = os.path.dirname(settings.paths['database'])
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Создаем движок базы данных
    engine = create_engine(
        settings.database['url'],
        echo=settings.database['echo']
    )
    
    # Создаем все таблицы
    SQLModel.metadata.create_all(engine)
    
    # Загружаем данные работ из JSON файла
    load_works_from_json(engine)
    
    print("База данных инициализирована успешно!")


def load_works_from_json(engine):
    """Загрузка работ из JSON файла в базу данных"""
    
    # Путь к файлу с данными работ
    works_file = os.path.join(os.path.dirname(__file__), '../data/works_full.json')
    
    with open(works_file, 'r', encoding='utf-8') as f:
        works_data = json.load(f)
    
    with Session(engine) as session:
        # Проверяем, есть ли уже работы в базе
        existing_works = session.query(Work).count()
        
        if existing_works > 0:
            print(f"В базе данных уже есть {existing_works} работ. Пропускаем загрузку.")
            return
        
        # Загружаем работы
        for work_data in works_data:
            work = Work(
                code=work_data['code'],
                name=work_data['name'],
                category=WorkCategory(work_data['category']),
                work_type=WorkType(work_data['work_type']),
                periodicity=work_data['periodicity'],
                regulations=work_data['regulations'],
                unit=work_data['unit'],
                formula=work_data['formula'],
                min_wear=work_data['min_wear'],
                max_wear=work_data['max_wear'],
                requires_oss=work_data['requires_oss'],
                critical=work_data['critical']
            )
            
            session.add(work)
        
        session.commit()
        print(f"Загружено {len(works_data)} работ в базу данных.")


if __name__ == "__main__":
    init_database()