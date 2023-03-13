FROM python:3.10-slim

RUN pip install --upgrade pip
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY .. .
WORKDIR /app/src
CMD gunicorn -b 0.0.0.0:8000 main:app -k uvicorn.workers.UvicornWorker
