FROM python:3.10-slim

# Установка зависимостей системы
RUN apt-get update && \
    apt-get install -y tesseract-ocr poppler-utils && \
    apt-get clean

# Копируем файлы проекта
WORKDIR /app
COPY . /app

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt

# Порт
EXPOSE 8501

# Запуск Streamlit
CMD ["streamlit", "run", "streamlit_interface.py"]
