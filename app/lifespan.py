# lifespan.py

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация ресурсов
    logger.info("Starting up...")
    # Можно добавить любую инициализацию, например, подключение к БД, кэширование и т.д.

    yield  # Запуск приложения

    # Очистка ресурсов
    logger.info("Shutting down...")
    # Можно добавить код для закрытия подключений к базе данных, завершения кэширования и т.д.
