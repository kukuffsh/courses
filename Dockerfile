#slim - облегченная версия
FROM python:3.11-slim

WORKDIR /src

#копируем и устанавливаем все необходимые библиотеки
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /src
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
