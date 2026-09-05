# Use official Python 3.11 slim image (Linux amd64 compatible)
FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable unbuffered console logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Set working directory inside container
WORKDIR /app

# Install minimal OS build dependencies for compiling Python packages if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first to leverage Docker layer caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download SentenceTransformer model weights into container image to eliminate runtime network latency
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy backend application source code
COPY . /app/

# Expose default Cloud Run port
EXPOSE 8080

# Start Gunicorn server binding dynamically to $PORT with 120s timeout
CMD exec gunicorn --bind 0.0.0.0:${PORT:-8080} --timeout 120 app:app
