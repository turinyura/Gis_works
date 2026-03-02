"""
Настройки приложения МКД-Менеджер
"""

import yaml
import os
from pathlib import Path


class Settings:
    def __init__(self):
        # Загружаем настройки из YAML файла
        config_path = Path(__file__).parent / "settings.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Извлекаем секции конфигурации
        self.app = self.config.get('app', {})
        self.database = self.config.get('database', {})
        self.paths = self.config.get('paths', {})
        self.defaults = self.config.get('defaults', {})


# Глобальный объект настроек
settings = Settings()