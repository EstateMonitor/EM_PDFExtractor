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
    version="0.0.1",
    docs_url="/docs",  # URL для доступа к Swagger UI
)

# Подключение функции жизненного цикла
app.lifespan = lifespan

# Подключение роутеров
app.include_router(pdf_router)

# Nuitka Project Options

# Опции компиляции для различных ОС
# nuitka-project-if: {OS} in ("Windows", "Linux"):
#   nuitka-project: --onefile
# nuitka-project-else:
#   nuitka-project: --standalone

# Включение данных и файлов конфигурации
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/config.yml=config.yml
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/core/config=core/config
if __name__ == "__main__":
    # Запуск приложения
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, log_level=config.LOG_LEVEL, reload=config.RELOAD)
