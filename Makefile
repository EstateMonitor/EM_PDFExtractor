# Makefile

# Название образа
IMAGE_NAME=em_pdf_extractor

# Цель по умолчанию
all: build

# Сборка Docker-образа
build:
	@echo "Building Docker image..."
	docker build -t $(IMAGE_NAME) .

# Запуск контейнера
run:
	@echo "Running Docker container..."
	docker run --rm -it $(IMAGE_NAME)

# Очистка сгенерированных файлов и образов Docker
clean:
	@echo "Cleaning up..."
	docker rmi $(IMAGE_NAME)
	rm -rf dist build __pycache__ *.dist-info

# Компиляция проекта без Docker
compile:
	@echo "Compiling project with Nuitka..."
	python -m nuitka --follow-imports main.py

# Сборка Docker-образа с использованием Nuitka
docker-compile:
	@echo "Building Docker image with Nuitka..."
	docker build --no-cache -t $(IMAGE_NAME)-compiled -f Dockerfile.nuitka .

# Запуск скомпилированного Docker-образа
docker-run-compiled:
	@echo "Running compiled Docker container..."
	docker run --rm -it $(IMAGE_NAME)-compiled

# Очистка всего
deep-clean: clean
	@echo "Removing all Docker images..."
	docker rmi $(IMAGE_NAME)-compiled
