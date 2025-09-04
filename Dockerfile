# Use Python 3.11 slim
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install git and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies (PyTgCalls dev6 + compatible aiohttp)
RUN pip install --no-cache-dir \
    git+https://github.com/pytgcalls/pytgcalls.git@dev \
    pyrogram==2.0.106 \
    tgcrypto \
    python-dotenv \
    aiohttp>=3.9.3

# Copy bot code
COPY . .

# Start bot
CMD ["python", "bot.py"]
