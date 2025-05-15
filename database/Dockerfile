# Start FROM official PostgreSQL image
FROM postgres:13

# Install system dependencies (Python, Redis, etc.)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    redis-server \
    netcat-traditional \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY ./system/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy all app code into container
COPY . .

# Copy and enable custom entrypoint
COPY ./system/entrypoint.sh /docker-entrypoint-initdb.d/entrypoint.sh
RUN chmod +x /docker-entrypoint-initdb.d/entrypoint.sh
