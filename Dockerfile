FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (kalau perlu untuk torch/transformers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements dulu untuk caching layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file project
COPY . .

# Set environment variable
ENV PYTHONUNBUFFERED=1

# Jalankan aplikasi
CMD ["python", "app.py"]