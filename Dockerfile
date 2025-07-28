# Use Python slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install system dependencies needed for Tamarin
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Tamarin Prover
RUN wget https://github.com/tamarin-prover/tamarin-prover/releases/download/1.8.0/tamarin-prover-1.8.0-linux64-ubuntu.tar.gz \
    && tar -xzf tamarin-prover-1.8.0-linux64-ubuntu.tar.gz \
    && mv tamarin-prover-1.8.0-linux64-ubuntu/bin/tamarin-prover /usr/local/bin/ \
    && chmod +x /usr/local/bin/tamarin-prover \
    && rm -rf tamarin-prover-1.8.0-linux64-ubuntu*

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
