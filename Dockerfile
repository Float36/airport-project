FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1    # ignore .pyc (bitcode)

ENV PYTHONUNBUFFERED 1          # logs without buffering

# install dependencies
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev \
    && apt-get clean

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .