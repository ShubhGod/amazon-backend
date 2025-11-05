# Use official Python 3.12 slim image
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version, increase timeout and retries
RUN pip install --upgrade pip
RUN pip config set global.timeout 120
RUN pip config set global.retries 5
RUN pip config set global.connect-timeout 60

# Copy requirements.txt file
COPY requirements.txt /app/

# Install Python packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app/
COPY data /app/data

# Expose FastAPI default port 8000
EXPOSE 8000

# Command to run the API server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
