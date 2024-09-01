# Используем легковесный базовый образ Alpine для стадии сборки
FROM python:3.11-alpine as builder

# Устанавливаем необходимые пакеты для Alpine и Nuitka
RUN apk update && apk add --no-cache \
    build-base \
    python3-dev \
    py3-pip \
    py3-setuptools \
    py3-wheel \
    curl \
    musl-dev \
    libffi-dev \
    openssl-dev \
    patchelf

# Устанавливаем pip и другие зависимости
RUN pip install --upgrade pip

# Копируем файлы проекта в контейнер
WORKDIR /app
COPY . /app

# Создаем виртуальное окружение и устанавливаем зависимости
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install -r requirements.txt && \
    pip install nuitka  # Устанавливаем Nuitka в виртуальное окружение

# Компиляция проекта с помощью Nuitka
RUN . venv/bin/activate && \
    venv/bin/python3 -m nuitka --follow-imports --report=compilation-report.xml main.py

# Собираем минимальный образ для запуска приложения
FROM alpine:latest as runtime

# Устанавливаем необходимые библиотеки для запуска Python
RUN apk add --no-cache libstdc++ libgcc

# Копируем скомпилированный бинарник и конфигурационные файлы в минимальный образ
WORKDIR /app
COPY --from=builder /app/main.bin /app/
COPY --from=builder /app/config.yml /app/
COPY --from=builder /app/core/config /app/core/config
COPY --from=builder /app/static /app/static
COPY --from=builder /app/compilation-report.xml /app/

# Устанавливаем точку входа
ENTRYPOINT ["/app/main.bin"]
