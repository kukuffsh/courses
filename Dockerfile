# Используем официальный образ Python
FROM python:3.8

# Устанавливаем рабочую директорию в контейнере
WORKDIR /src

# Копируем локальный requirements.txt в контейнер
COPY requirements.txt /src/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . /app/

# Указываем команду для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
