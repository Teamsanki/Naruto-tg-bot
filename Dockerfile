# Python 3.11 base image
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

# Copy requirements
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir \
    git+https://github.com/pytgcalls/pytgcalls.git@dev \
    pyrogram==2.0.106 \
    tgcrypto \
    python-dotenv \
    aiohttp==3.8.5

# Copy bot code
COPY . .

# Set environment variables (optional, or use .env)
# ENV API_ID=123456
# ENV API_HASH=abcdef123456
# ENV BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Start bot
CMD ["python", "bot.py"]
