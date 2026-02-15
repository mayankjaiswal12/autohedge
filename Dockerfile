FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages || pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Create output directory
RUN mkdir -p /app/outputs /app/data

# Expose port
EXPOSE 8000

# Keep container running - it will be started via make dashboard
CMD ["tail", "-f", "/dev/null"]
