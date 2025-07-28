# syntax=docker/dockerfile:1
# force AMD64 so we can always pull the AMD64 Verifpal binary
FROM --platform=linux/amd64 python:3.11-slim

# Install system deps
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    pkg-config \
    libssl-dev \
  && rm -rf /var/lib/apt/lists/*

# Fetch & install Verifpal v0.26.0 (AMD64)
/usr/bin/curl -L \
    https://github.com/symbolicsoft/verifpal/releases/download/v0.26.0/verifpal_linux_amd64 \
  -o /usr/local/bin/verifpal \
  && chmod +x /usr/local/bin/verifpal

# Create app dir
WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Your Flask app
COPY app.py .

# Expose & run
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
