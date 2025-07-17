FROM python:3.11-slim

# Устанавливаем системные зависимости, включая русскую локализацию для tesseract
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    tesseract-ocr \
    tesseract-ocr-rus \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Rust для сборки pydantic-core
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Копируем код проекта
COPY . .

# Запускаем приложение
CMD ["python", "Pravdabot.py"]
