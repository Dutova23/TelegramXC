# Используем стабильный образ Python
FROM python:3.11-slim

# Установка зависимостей системы (для tesseract и Pillow)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Создание директории приложения
WORKDIR /app

# Копируем зависимости и проект
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Команда запуска (замени на свой основной файл)
CMD ["python", "main.py"]
