FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        python3-dev \
        musl-dev \
        libpq-dev \
        gettext \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt
COPY requirements.txt /app/

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . /app/

# Создаем необходимые директории
RUN mkdir -p /app/static /app/media /app/logs

# Создаем скрипт для запуска
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Создаем непривилегированного пользователя
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Открываем порт
EXPOSE 8000

# Запускаем приложение
ENTRYPOINT ["/entrypoint.sh"] 