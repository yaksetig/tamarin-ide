FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    HOMEBREW_PREFIX=/home/linuxbrew/.linuxbrew \
    PATH=/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:/usr/local/bin:/usr/bin:/bin

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      curl \
      file \
      git \
      procps \
      sudo \
      python3 \
      python3-pip \
      ca-certificates \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m brewuser && echo "brewuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER brewuser
WORKDIR /home/brewuser

RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

RUN brew tap tamarin-prover/tap && brew install tamarin-prover

RUN tamarin-prover --version

USER root
WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE ${PORT}
CMD ["python", "app.py"]
