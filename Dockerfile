# Use Ubuntu 22.04 - Tamarin is built for Ubuntu
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
    && rm -rf /var/lib/apt/lists/*

# Install Tamarin Prover - try multiple approaches
RUN cd /tmp && \
    echo "Downloading Tamarin Prover..." && \
    # First try: Version 1.8.0
    ( wget --no-check-certificate -O tamarin.tar.gz \
      "https://github.com/tamarin-prover/tamarin-prover/releases/download/1.8.0/tamarin-prover-1.8.0-linux64-ubuntu.tar.gz" && \
      echo "Downloaded successfully, extracting..." && \
      tar -xzf tamarin.tar.gz && \
      echo "Files extracted:" && \
      ls -la && \
      echo "Looking for tamarin-prover binary..." && \
      find . -name "tamarin-prover" -type f && \
      # Try different possible paths
      if [ -f "tamarin-prover-1.8.0-linux64-ubuntu/bin/tamarin-prover" ]; then \
        cp tamarin-prover-1.8.0-linux64-ubuntu/bin/tamarin-prover /usr/local/bin/; \
      elif [ -f "bin/tamarin-prover" ]; then \
        cp bin/tamarin-prover /usr/local/bin/; \
      elif [ -f "tamarin-prover" ]; then \
        cp tamarin-prover /usr/local/bin/; \
      else \
        echo "Binary not found in expected locations, searching..."; \
        find . -name "tamarin-prover" -executable -exec cp {} /usr/local/bin/ \;; \
      fi \
    ) || \
    # Fallback: Try version 1.6.1
    ( echo "Trying version 1.6.1..." && \
      wget --no-check-certificate -O tamarin.tar.gz \
      "https://github.com/tamarin-prover/tamarin-prover/releases/download/1.6.1/tamarin-prover-1.6.1-linux64-ubuntu.tar.gz" && \
      tar -xzf tamarin.tar.gz && \
      find . -name "tamarin-prover" -executable -exec cp {} /usr/local/bin/ \; \
    ) || \
    # Last resort: Install via apt if available
    ( echo "Trying package manager..." && \
      apt-get update && \
      apt-get install -y tamarin-prover \
    )

# Make executable and verify
RUN chmod +x /usr/local/bin/tamarin-prover && \
    echo "Verifying Tamarin installation..." && \
    ls -la /usr/local/bin/tamarin-prover && \
    /usr/local/bin/tamarin-prover --version

# Clean up
RUN rm -rf /tmp/* && apt-get clean

# Create python symlink
RUN ln -sf /usr/bin/python3 /usr/bin/python

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
