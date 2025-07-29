# Multi-stage build to get Tamarin working
FROM haskell:8.10 as tamarin-builder

# Install dependencies for building Tamarin
RUN apt-get update && apt-get install -y \
    git \
    make \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Clone and build Tamarin from source
RUN git clone --depth 1 --branch master https://github.com/tamarin-prover/tamarin-prover.git /tmp/tamarin && \
    cd /tmp/tamarin && \
    make default && \
    cp dist/build/tamarin-prover/tamarin-prover /usr/local/bin/

# Final stage with Python
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Copy Tamarin from builder stage
COPY --from=tamarin-builder /usr/local/bin/tamarin-prover /usr/local/bin/
RUN chmod +x /usr/local/bin/tamarin-prover

# Verify Tamarin works
RUN tamarin-prover --version

# Create python symlink
RUN ln -sf /usr/bin/python3 /usr/bin/python

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE $PORT

CMD python app.py
