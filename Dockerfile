# Use Python 3.11 base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
# PyTgCalls dev6 directly from GitHub to avoid tgcalls PyPI issue
RUN pip install --no-cache-dir \
    git+https://github.com/pytgcalls/pytgcalls.git@dev \
    pyrogram==2.0.106 \
    tgcrypto \
    python-dotenv \
    aiohttp==3.8.5

# Copy all bot files
COPY . .

# Expose port if bot uses webhooks (optional)
# EXPOSE 8080

# Set environment variables here or use .env file
# ENV API_ID=123456
# ENV API_HASH=abcdef123456
# ENV BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Start bot
CMD ["python", "bot.py"]
