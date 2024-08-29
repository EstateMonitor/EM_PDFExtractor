# main.py

import uvicorn
from fastapi import FastAPI

from app.api.routers.pdf_router import router as pdf_router
from app.lifespan import lifespan
from core.config import config

# Создание экземпляра FastAPI с дополнительной конфигурацией для документации
app = FastAPI(
    title="PDF Processing Service",
    description="API для обработки PDF-файлов о простое лифтов.",
    version="1.0.0",
    docs_url="/docs",  # URL для доступа к Swagger UI
    redoc_url="/redoc"  # URL для доступа к ReDoc
)

# Подключение функции жизненного цикла
app.lifespan = lifespan

# Подключение роутеров
app.include_router(pdf_router)

if __name__ == "__main__":
    # Запуск приложения
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, log_level=config.LOG_LEVEL, reload=config.RELOAD)
