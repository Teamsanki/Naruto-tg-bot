# Base image Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Set environment variables (optional, can also use .env)
# ENV API_ID=123456
# ENV API_HASH=abcdef123456
# ENV BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Start bot
CMD ["python", "bot.py"]
