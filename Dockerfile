# Use Ubuntu base - Tamarin is built for Ubuntu
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Try installing Tamarin from multiple sources
RUN cd /tmp && \
    # Try version 1.6.1 first (older but more stable)
    ( wget "https://github.com/tamarin-prover/tamarin-prover/releases/download/1.6.1/tamarin-prover-1.6.1-linux64-ubuntu.tar.gz" && \
      tar -xzf tamarin-prover-1.6.1-linux64-ubuntu.tar.gz && \
      cp tamarin-prover-1.6.1-linux64-ubuntu/bin/tamarin-prover /usr/local/bin/ \
    ) || \
    # Fallback to direct binary download
    ( wget "https://github.com/tamarin-prover/tamarin-prover/releases/download/1.8.0/tamarin-prover-1.8.0-linux64-ubuntu.tar.gz" && \
      tar -xzf tamarin-prover-1.8.0-linux64-ubuntu.tar.gz && \
      cp tamarin-prover-1.8.0-linux64-ubuntu/bin/tamarin-prover /usr/local/bin/ \
    ) || \
    # Last resort: try to get from CI builds
    ( echo "Trying alternative download..." && \
      wget -O tamarin-bin "https://github.com/tamarin-prover/tamarin-prover/releases/download/1.6.1/tamarin-prover-1.6.1-linux64-ubuntu.tar.gz" && \
      tar -xzf tamarin-bin && \
      find . -name "tamarin-prover" -executable -type f -exec cp {} /usr/local/bin/ \; \
    )

# Make executable and test
RUN chmod +x /usr/local/bin/tamarin-prover && \
    ls -la /usr/local/bin/tamarin-prover && \
    tamarin-prover --version

# Python setup
RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE $PORT

CMD python app.py
