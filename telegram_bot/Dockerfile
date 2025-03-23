FROM python:3.11-slim

# Установка зависимостей
WORKDIR /app
COPY telegram_bot/ /app/telegram_bot
COPY ./telegram_bot/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Настройка PYTHONPATH, чтобы видеть telegram_bot как пакет
ENV PYTHONPATH=/app

# Запуск
CMD ["python", "-m", "telegram_bot.bot"]
