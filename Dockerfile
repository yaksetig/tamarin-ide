FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Install minimal dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Download and install Tamarin binary directly
RUN curl -L https://github.com/tamarin-prover/tamarin-prover/releases/download/1.6.1/tamarin-prover-1.6.1-linux64-ubuntu.tar.gz | tar -xz -C /tmp && \
    cp /tmp/tamarin-prover-1.6.1-linux64-ubuntu/bin/tamarin-prover /usr/local/bin/ && \
    chmod +x /usr/local/bin/tamarin-prover && \
    rm -rf /tmp/tamarin*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE $PORT
CMD python app.py
