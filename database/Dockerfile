# Use slim Debian base
FROM debian:bullseye-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies including PostgreSQL and Redis
RUN apt-get update && apt-get install -y \
    postgresql \
    redis-server \
    gcc \
    python3 \
    python3-pip \
    libpq-dev \
    netcat-traditional

# Install Python dependencies
COPY ./system/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Copy and apply the custom pg_hba.conf for PostgreSQL 13
COPY ./system/pg_hba.conf /etc/postgresql/13/main/pg_hba.conf
RUN chown postgres:postgres /etc/postgresql/13/main/pg_hba.conf

# Expose Flask, PostgreSQL, and Redis ports
EXPOSE 5003 5432 6379

# Copy and prepare entrypoint script
COPY ./system/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Start services and app
CMD ["/entrypoint.sh"]
