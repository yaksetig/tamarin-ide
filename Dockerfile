FROM ubuntu:22.04

# 1. Install Homebrew prerequisites
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      curl \
      file \
      git \
      procps \
      sudo \
    && rm -rf /var/lib/apt/lists/*

# 2. Create a non‑root user for Homebrew (recommended)
RUN useradd -m brewuser && echo "brewuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER brewuser
WORKDIR /home/brewuser

# 3. Install Homebrew
RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" \
  && echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile

# 4. Load Homebrew environment and install Tamarin
ENV PATH="/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:${PATH}"
RUN . ~/.profile && \
    brew tap tamarin-prover/tap && \
    brew install tamarin-prover

# 5. Verify
RUN tamarin-prover --version

# (…rest of your Dockerfile…)
