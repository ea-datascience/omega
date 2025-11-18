FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Install minimal system packages including Java 17
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        # Basic utilities
        curl \
        wget \
        jq \
        unzip \
        vim \
        nano \
        tree \
        git \
        # Java Development Kit 17
        openjdk-17-jdk \
        openjdk-17-jre \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
ENV PATH=$JAVA_HOME/bin:$PATH

# Install uv globally so all users can access it
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    cp /root/.local/bin/uv /usr/local/bin/uv && \
    chmod +x /usr/local/bin/uv

# Configure shell profiles for automatic virtual environment activation
RUN echo 'if [ -f /workspace/.venv/bin/activate ]; then source /workspace/.venv/bin/activate; fi' >> /home/vscode/.bashrc && \
    echo 'if [ -f /workspace/.venv/bin/activate ]; then source /workspace/.venv/bin/activate; fi' >> /home/vscode/.zshrc

# Create workspace directory
WORKDIR /workspace