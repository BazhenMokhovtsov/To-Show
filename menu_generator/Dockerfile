FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN python3 -m pip install --no-cache-dir --no-warn-script-location --upgrade pip

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN python3 -m pip install --no-cache-dir --no-warn-script-location -r requirements.txt

COPY . .

RUN chmod -R 777 ./
