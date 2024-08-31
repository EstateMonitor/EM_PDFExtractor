# Используем официальный образ Python для сборки
FROM python:3.11-slim as builder

# Устанавливаем необходимые пакеты для компиляции
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости проекта
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем исходный код проекта
COPY . /app

# Компилируем Python код в C-расширения с использованием Cython
RUN cythonize -i -3 -b .

# Удаляем исходные .py файлы, оставляем только скомпилированные файлы
RUN find . -name "*.py" -type f -delete

# Используем минимальный образ для финального контейнера
FROM python:3.11-slim

# Копируем скомпилированные файлы из builder этапа
COPY --from=builder /app /app

# Устанавливаем минимальные необходимые пакеты
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt --no-cache-dir

# Устанавливаем рабочую директорию
WORKDIR /app

# Указываем команду для запуска приложения
CMD ["python", "main.py"]
