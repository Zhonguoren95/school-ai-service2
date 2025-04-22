FROM python:3.11-slim

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    build-essential \
    libpoppler-cpp-dev \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Указываем порт для Streamlit
EXPOSE 8501

# Команда запуска Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.enableCORS=false"]
