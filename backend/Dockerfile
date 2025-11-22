FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium only for smaller image)
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/recordings /app/demo-environments /app/audio_cache && \
    chmod 777 /app/recordings /app/demo-environments /app/audio_cache

# Expose port (Railway will override with $PORT)
EXPOSE 8000

# Run the application
# Use PORT environment variable from Railway, fallback to 8000 for local
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
