FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/app/.cache/huggingface

CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 app:app