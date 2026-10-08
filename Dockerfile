# 1. Берем базовый официальный образ Python
FROM python:3.12-slim

# 2. Устанавливаем рабочую папку внутри контейнера
WORKDIR /app

# 3. Отключаем кэширование Питона, чтобы логи выводились сразу
ENV PYTHONUNBUFFERED=1

# 4. Копируем файл с библиотеками и устанавливаем их внутри контейнера
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем весь наш код в контейнер
COPY . .

# 6. Команда, которая запустит сервер внутри контейнера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]