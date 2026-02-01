FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY autohedge/ ./autohedge/
COPY setup.py .
RUN pip install -e .

RUN mkdir -p outputs agent_workspace

ENV OLLAMA_URL=http://ollama:11434
ENV OLLAMA_MODEL=qwen2.5:7b

CMD ["/bin/bash"]
