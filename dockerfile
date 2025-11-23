# Dockerfile for RAG API Backend
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ ./app/
COPY chunks.jsonl .
COPY chroma_db/ ./chroma_db/

# Expose port
EXPOSE 8000

# Set environment variable for API key (will be overridden by docker-compose)
ENV GOOGLE_API_KEY=""

# Run the application
CMD ["python", "app/main.py"]
