FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTCODE 1    # ignore .pyc (bitcode)

ENV PYTHONUNBUFFERED 1          # logs without buffering

RUN apt-get update \
    && apt-get install -y build-essential libpq-dev \       # install dependencies
    && apt-get clean

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .