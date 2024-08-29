# core/config.py

import os
from pathlib import Path

from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """
    Класс конфигурации для хранения всех настроек приложения.
    """
    APP_NAME = os.getenv("APP_NAME", "PDF Extractor")
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    RELOAD = bool(os.getenv("RELOAD", True))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")


config = Config()
