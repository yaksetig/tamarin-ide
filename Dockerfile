# Use Ubuntu base for better Tamarin compatibility
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    curl \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Tamarin Prover - using the exact working method
RUN cd /tmp && \
    wget -O tamarin.tar.gz "https://github.com/tamarin-prover/tamarin-prover/releases/download/1.8.0/tamarin-prover-1.8.0-linux64-ubuntu.tar.gz" && \
    ls -la tamarin.tar.gz && \
    tar -tzf tamarin.tar.gz | head -10 && \
    tar -xzf tamarin.tar.gz && \
    ls -la && \
    find . -name "*tamarin*" -type d && \
    find . -name "tamarin-prover" -type f && \
    cp tamarin-prover-1.8.0-linux64-ubuntu/bin/tamarin-prover /usr/local/bin/ && \
    chmod +x /usr/local/bin/tamarin-prover && \
    rm -rf /tmp/tamarin* && \
    tamarin-prover --version

# Create symlink for python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE $PORT

# Run the application
CMD python app.py
