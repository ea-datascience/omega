# Analysis Engine Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for analysis tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    unzip \
    openjdk-17-jdk \
    graphviz \
    graphviz-dev \
    pkg-config \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Install CodeQL CLI
RUN wget -q https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip \
    && unzip codeql-linux64.zip \
    && mv codeql /usr/local/bin/ \
    && rm codeql-linux64.zip

# Install Context Mapper CLI
RUN wget -q https://github.com/ContextMapper/context-mapper-cli/releases/latest/download/context-mapper-cli.jar -O /usr/local/bin/context-mapper-cli.jar \
    && echo '#!/bin/bash\njava -jar /usr/local/bin/context-mapper-cli.jar "$@"' > /usr/local/bin/context-mapper \
    && chmod +x /usr/local/bin/context-mapper

# Install Structurizr CLI
RUN wget -q https://github.com/structurizr/cli/releases/latest/download/structurizr-cli.zip \
    && unzip structurizr-cli.zip \
    && mv structurizr-cli-*.jar /usr/local/bin/structurizr-cli.jar \
    && echo '#!/bin/bash\njava -jar /usr/local/bin/structurizr-cli.jar "$@"' > /usr/local/bin/structurizr \
    && chmod +x /usr/local/bin/structurizr \
    && rm structurizr-cli.zip

# Install Microsoft AppCAT
RUN wget -q https://github.com/Azure/appcat/releases/latest/download/appcat-linux-x64.tar.gz \
    && tar -xzf appcat-linux-x64.tar.gz \
    && mv appcat /usr/local/bin/ \
    && chmod +x /usr/local/bin/appcat \
    && rm appcat-linux-x64.tar.gz

# Copy Python requirements and install
COPY pyproject.toml /app/
RUN pip install --no-cache-dir -e .[dev]

# Copy application source
COPY src/ /app/src/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/

# Create cache and artifacts directories
RUN mkdir -p /app/cache /app/artifacts

# Set Python path
ENV PYTHONPATH=/app/src

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "omega_analysis.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]