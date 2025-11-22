FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (we should create this too)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for file storage
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV STORAGE_TYPE=file
ENV DATA_DIR=/app/data
ENV LOG_LEVEL=INFO

# Expose ports for SIEM integration
EXPOSE 5000

# Run tests by default (can be overridden)
CMD ["python", "-m", "unittest", "discover", "-s", "utils/tests", "-p", "test_*.py", "-v"]