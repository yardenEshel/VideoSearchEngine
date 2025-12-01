FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    ffmpeg \
    libvips \
    libvips-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set default python
RUN ln -s /usr/bin/python3.10 /usr/bin/python

WORKDIR /app

COPY requirements.txt .

# FIX: Removed "--break-system-packages"
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/main.py"]