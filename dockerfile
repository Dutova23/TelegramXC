# Базовый образ с Python
FROM python:3.12-slim

# Устанавливаем зависимости для Pillow и Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создаём рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip setuptools wheel
RUN pip install --only-binary=:all: -r requirements.txt

# Стартовая команда
CMD ["python", "Pravdabot.py"]
