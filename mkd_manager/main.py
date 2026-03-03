"""
Точка входа в приложение МКД-Менеджер
"""
import sys
import os
from mkd_manager.config import settings
from mkd_manager.core.application import Application
from mkd_manager.database.connection import init_database
from mkd_manager.gui.main_window import MainWindow
import logging


def setup_logging():
    """Настройка системы логирования"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Основная функция запуска приложения"""
    try:
        # Инициализация настроек
        print(f"Загрузка конфигурации из {settings.CONFIG_PATH}")
        
        # Настройка логирования
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Запуск приложения МКД-Менеджер")
        
        # Инициализация базы данных
        init_database()
        logger.info("База данных инициализирована")
        
        # Запуск GUI приложения
        app = Application()
        window = MainWindow()
        window.show()
        logger.info("Графический интерфейс запущен")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        logging.error(f"Критическая ошибка при запуске: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()