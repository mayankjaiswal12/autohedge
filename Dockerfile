FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /app/venv
RUN /app/venv/bin/pip install --upgrade pip
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY autohedge/ ./autohedge/
COPY setup.py .

# Install autohedge in the virtual environment
RUN /app/venv/bin/pip install -e .

# Create output directories
RUN mkdir -p outputs agent_workspace

# Set environment variables
ENV OLLAMA_URL=http://ollama:11434
ENV OLLAMA_MODEL=qwen2.5:7b
ENV PATH="/app/venv/bin:$PATH"

# Default command
CMD ["/bin/bash"]
