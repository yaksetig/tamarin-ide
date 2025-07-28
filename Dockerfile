# Use Python slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Try alternative Tamarin installation method
RUN set -e && \
    cd /tmp && \
    # Try direct download with progress
    wget --progress=dot:giga --timeout=60 --tries=2 \
    "https://github.com/tamarin-prover/tamarin-prover/releases/download/1.8.0/tamarin-prover-1.8.0-linux64-ubuntu.tar.gz" \
    -O tamarin.tar.gz && \
    echo "Download complete, extracting..." && \
    tar -xzf tamarin.tar.gz && \
    echo "Extraction complete, installing..." && \
    cp tamarin-prover-1.8.0-linux64-ubuntu/bin/tamarin-prover /usr/local/bin/ && \
    chmod +x /usr/local/bin/tamarin-prover && \
    echo "Cleaning up..." && \
    rm -rf /tmp/tamarin* && \
    echo "Testing installation..." && \
    tamarin-prover --version && \
    echo "Tamarin installation successful!"

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE $PORT

# Run the application
CMD python app.py
