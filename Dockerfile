LABEL authors="Fascinat0r"
# Этап 1: Сборка исполняемого файла с помощью PyInstaller
FROM python:3.10-slim AS builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости для PyInstaller
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем PyInstaller
RUN pip install --no-cache-dir pyinstaller

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения в контейнер
COPY . .

# Собираем исполняемый файл приложения с помощью PyInstaller
RUN pyinstaller --onefile --name pdf_extractor main.py

# Этап 2: Создание минимального Docker-образа для запуска приложения
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем исполняемый файл из этапа сборки
COPY --from=builder /app/dist/pdf_extractor .

# Устанавливаем переменные окружения для FastAPI
ENV PYTHONUNBUFFERED=1

# Указываем команду для запуска исполняемого файла
CMD ["./pdf_extractor"]
