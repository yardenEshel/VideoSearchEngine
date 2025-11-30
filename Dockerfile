FROM python:3.10-slim

# Install system dependencies (FFmpeg is critical for yt-dlp and scenedetect)
# libgl1 and libglib2.0-0 are often required for OpenCV inside Docker
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# We include --no-cache-dir to keep the image smaller, though for dev it matters less
RUN pip install --no-cache-dir -r requirements.txt

# We don't COPY src/ here because we will mount it via docker-compose 
# to allow editing code without rebuilding the image.

CMD ["python", "src/main.py"]

