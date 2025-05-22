FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Add app to PYTHONPATH
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libffi-dev \
    curl \
    git \
    ca-certificates \
    gnupg \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm globally
RUN npm install -g pnpm

# Clone and build anime-captcha
RUN git clone https://github.com/leomotors/anime-captcha.git /app/anime-captcha && \
    cd /app/anime-captcha && \
    pnpm install && \
    pnpm build

# Copy requirements and install Python dependencies
COPY ./system/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app

# Copy entrypoint script and make it executable
COPY ./system/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Run entrypoint
ENTRYPOINT ["/entrypoint.sh"]
