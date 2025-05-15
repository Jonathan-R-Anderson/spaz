FROM python:3.9-slim

WORKDIR /app

# Install Redis (client-only if needed), netcat for readiness checks
RUN apt-get update && apt-get install -y \
    redis-server \
    netcat-traditional \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY ./system/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Expose Flask API port
EXPOSE 5003

# Entrypoint to start Flask + Redis etc.
COPY ./system/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
