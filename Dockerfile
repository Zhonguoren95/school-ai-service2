FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libjpeg-dev \
    gcc \
    && apt-get clean

# Рабочая директория
WORKDIR /app

# Копирование всех файлов проекта
COPY . /app

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Открываемый порт
EXPOSE 8501

# Команда запуска Streamlit
CMD ["streamlit", "run", "streamlit_interface.py"]
