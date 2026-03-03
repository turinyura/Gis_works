-- Database Schema for Work Descriptions
-- Specifically designed to store detailed work descriptions like the emergency dispatcher service

CREATE TABLE IF NOT EXISTS work_descriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_number VARCHAR(10) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    purpose TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS legal_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id INTEGER,
    document_name TEXT NOT NULL,
    article_section TEXT,
    FOREIGN KEY (work_id) REFERENCES work_descriptions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS work_objectives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id INTEGER,
    objective TEXT NOT NULL,
    FOREIGN KEY (work_id) REFERENCES work_descriptions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS request_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id INTEGER,
    category VARCHAR(50) NOT NULL,
    examples TEXT,
    priority_level VARCHAR(20),
    response_time VARCHAR(20),
    FOREIGN KEY (work_id) REFERENCES work_descriptions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS work_stages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id INTEGER,
    stage_number INTEGER,
    stage_name TEXT NOT NULL,
    duration_limit VARCHAR(20),
    description TEXT,
    FOREIGN KEY (work_id) REFERENCES work_descriptions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tools_equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id INTEGER,
    item_name TEXT NOT NULL,
    purpose TEXT,
    requirements TEXT,
    FOREIGN KEY (work_id) REFERENCES work_descriptions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quality_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id INTEGER,
    parameter_name TEXT NOT NULL,
    normative_value TEXT,
    critical_value TEXT,
    regulation_reference TEXT,
    FOREIGN KEY (work_id) REFERENCES work_descriptions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS kpi_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id INTEGER,
    kpi_name TEXT NOT NULL,
    target_value TEXT,
    calculation_method TEXT,
    FOREIGN KEY (work_id) REFERENCES work_descriptions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS responsibilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id INTEGER,
    position TEXT NOT NULL,
    duties TEXT,
    FOREIGN KEY (work_id) REFERENCES work_descriptions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS related_works (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id INTEGER,
    related_work_number VARCHAR(10),
    relationship_type TEXT,
    FOREIGN KEY (work_id) REFERENCES work_descriptions(id) ON DELETE CASCADE
);

-- Insert the emergency dispatcher service work description
INSERT INTO work_descriptions (work_number, title, description, purpose) VALUES 
('19', 'Прием и выполнение аварийно-диспетчерской службой заявок собственников и пользователей помещений в многоквартирных домах', 
 'Подробное описание работы аварийно-диспетчерской службы по приему и выполнению заявок от собственников помещений в многоквартирных домах, включая нормативное обоснование, цели, состав работ, инструменты, параметры контроля и этапы проведения.', 
 'Обеспечение круглосуточного приема обращений, оперативного реагирования на аварийные и неаварийные заявки, документирования всех обращений, координации действий исполнителей, информирования заявителей, соблюдения предельных сроков устранения неисправностей и повышения удовлетворенности собственников качеством услуг.');

-- Insert legal documents
INSERT INTO legal_documents (work_id, document_name, article_section) VALUES 
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Жилищный кодекс РФ', 'ст. 161'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Постановление Правительства РФ № 416', 'п. 23-25'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Постановление Правительства РФ № 354', 'п. 31, 104-108'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Постановление Госстроя РФ № 170', 'п. 3.2.1, 4.1'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'ГОСТ Р 56195-2014', 'Раздел 5'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'ГОСТ Р 51929-2002', 'п. 5.3.2'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Постановление Правительства РФ № 491', 'п. 10-11'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'СанПиН 2.1.2.2645-10', 'п. 4.2-4.6');

-- Insert work objectives
INSERT INTO work_objectives (work_id, objective) VALUES 
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Круглосуточного приема обращений собственников по вопросам неисправностей'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Оперативного реагирования на аварийные и неаварийные заявки'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Документирования всех обращений для учета и контроля'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Координации действий исполнителей (слесари, электрики, сантехники)'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Информирования заявителей о статусе выполнения работ'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Соблюдения предельных сроков устранения неисправностей'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Повышения удовлетворенности собственников качеством услуг');

-- Insert request types
INSERT INTO request_types (work_id, category, examples, priority_level, response_time) VALUES 
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Аварийная', 'Прорыв трубы, отключение электричества, утечка газа, затопление', 'Высший', '≤ 30 минут'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Срочная', 'Засор канализации, отсутствие ГВС, неисправность крана, поломка замка', 'Высокий', '≤ 2 часов'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Плановая', 'Замена лампочки, регулировка двери, мелкий ремонт, консультация', 'Средний', '≤ 24-72 часов'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Консультация', 'Вопросы по начислениям, порядку подачи показаний, график работ', 'Низкий', 'В день обращения');

-- Insert work stages
INSERT INTO work_stages (work_id, stage_number, stage_name, duration_limit, description) VALUES 
((SELECT id FROM work_descriptions WHERE work_number = '19'), 1, 'Прием обращения', 'до 5 минут', 'Принятие звонка/обращения, определение типа заявки, фиксация данных'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 2, 'Регистрация и классификация', 'до 5 минут', 'Присвоение уникального номера, внесение в CRM, определение приоритета'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 3, 'Назначение исполнителя', 'до 10 минут', 'Определение ответственной службы, назначение конкретного исполнителя'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 4, 'Контроль исполнения', 'в течение срока', 'Мониторинг статуса заявки, контроль сроков выполнения'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 5, 'Завершение и обратная связь', 'до 1 часа после выполнения', 'Получение отчета от исполнителя, обратная связь с заявителем'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 6, 'Аналитика и профилактика', 'ежемесячно', 'Формирование отчетов, выявление системных проблем');

-- Insert tools and equipment
INSERT INTO tools_equipment (work_id, item_name, purpose, requirements) VALUES 
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Диспетчерский пульт/CRM-система', 'Регистрация, учет, маршрутизация заявок', 'Интеграция с мобильными приложениями, резервное копирование'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'IP-телефония с записью разговоров', 'Прием звонков 24/7', 'Запись всех разговоров, резервный канал связи'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Мобильное приложение для исполнителей', 'Передача заявок, фотоотчеты, статусы', 'Геолокация, офлайн-режим, push-уведомления'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Система SMS/Email-уведомлений', 'Информирование заявителей', 'Интеграция с CRM, шаблоны сообщений'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'База знаний/скрипты', 'Стандартизация ответов диспетчеров', 'Актуальные инструкции, FAQ, регламенты'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Средства связи (рация/телефон)', 'Координирование с бригадами', 'Проверенная связь, резервные каналы'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Журналы (электронные/бумажные)', 'Фиксация обращений и действий', 'Прошнурованные, пронумерованные (для бумажных)'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'СИЗ для выездного персонала', 'Защита работников при выполнении заявок', 'По видам работ (электрика, сантехника и т.д.)');

-- Insert quality parameters
INSERT INTO quality_parameters (work_id, parameter_name, normative_value, critical_value, regulation_reference) VALUES 
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Время ответа на звонок', '≤ 30 секунд (95% звонков)', '> 60 секунд', 'ГОСТ Р 56195-2014'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Время регистрации заявки', '≤ 5 минут', '> 15 минут', 'Пост. № 354'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Время назначения исполнителя', '≤ 10 минут', '> 30 минут', 'ГОСТ Р 56195-2014'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Срок устранения аварии', '≤ 1 часа с момента регистрации', '> 2 часов', 'Пост. № 170, Пост. № 354'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Срок устранения срочной заявки', '≤ 24 часов', '> 48 часов', 'Пост. № 416'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Срок устранения плановой заявки', '≤ 3-5 рабочих дней', '> 10 дней', 'Договор управления'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Доступность службы', '24/7, 365 дней в году', 'Перерывы в работе', 'Пост. № 416'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Удовлетворенность заявителей', '≥ 4,5 из 5', '< 3,5 из 5', 'Внутренний регламент'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Процент повторных обращений', '≤ 5%', '> 15%', 'Внутренний регламент'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Доля закрытых заявок в срок', '≥ 95%', '< 85%', 'Внутренний регламент');

-- Insert KPI metrics
INSERT INTO kpi_metrics (work_id, kpi_name, target_value, calculation_method) VALUES 
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Время ответа на звонок', '≤ 30 сек (95% звонков)', '(Кол-во звонков с ответом ≤30 сек / Общее кол-во) × 100%'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Время регистрации заявки', '≤ 5 мин (100% заявок)', 'Фиксация в системе'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Соблюдение сроков аварийных заявок', '≥ 98%', '(Кол-во выполненных в срок / Общее кол-во аварийных) × 100%'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Соблюдение сроков срочных заявок', '≥ 95%', 'Аналогично'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Соблюдение сроков плановых заявок', '≥ 90%', 'Аналогично'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Удовлетворенность заявителей', '≥ 4,5 из 5', 'Опрос после закрытия заявки'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Процент повторных обращений', '≤ 5%', '(Кол-во повторных заявок / Общее кол-во) × 100%'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Доля заявок, выполненных с первого раза', '≥ 90%', '(Кол-во заявок без повторного выезда / Общее кол-во) × 100%'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Доступность службы', '99,9% времени', '(Время работы / Общее время) × 100%');

-- Insert responsibilities
INSERT INTO responsibilities (work_id, position, duties) VALUES 
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Диспетчер АДС', 'Прием звонков, регистрация заявок, классификация, назначение исполнителей, информирование заявителей, первичный контроль'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Старший диспетчер', 'Координация работы смены, разрешение сложных ситуаций, эскалация аварий, контроль KPI'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Исполнитель (слесарь/электрик/сантехник)', 'Выезд по заявкам, устранение неисправностей, оформление актов, фотоотчеты, соблюдение сроков'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Мастер участка/бригадир', 'Контроль качества работ исполнителей, анализ статистики, обучение персонала, планирование профилактики'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Руководитель УК', 'Организация процесса, утверждение регламентов, обеспечение ресурсами, работа с претензиями, отчетность перед собственниками'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), 'Собственник помещения', 'Предоставление доступа в помещение, корректное описание проблемы, соблюдение правил эксплуатации');

-- Insert related works
INSERT INTO related_works (work_id, related_work_number, relationship_type) VALUES 
((SELECT id FROM work_descriptions WHERE work_number = '19'), '14', 'Контроль инженерных систем → заявка на устранение неисправности'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), '15-18', 'Аварийно-диспетчерская служба → единый процесс приема и реагирования на аварии'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), '131', 'Обеспечение устранения аварий → координация при крупных авариях'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), '206-212', 'Работа с жалобами на качество КУ → прием и обработка обращений'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), '222', 'Выполнение заявок населения → обобщающая работа по всем заявкам'),
((SELECT id FROM work_descriptions WHERE work_number = '19'), '272', 'Содержание аварийно-диспетчерской службы → обеспечение работы диспетчерской');