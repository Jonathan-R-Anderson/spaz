# Use the official Python image
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
    libpq-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Copy the custom pg_hba.conf file
COPY pg_hba.conf /etc/postgresql/15/main/pg_hba.conf

# Set the appropriate permissions on the PostgreSQL configuration
RUN chown postgres:postgres /etc/postgresql/15/main/pg_hba.conf

# Expose necessary ports
EXPOSE 5003 5432 6379

# Create entrypoint script to start services
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Start the entrypoint script
CMD ["/entrypoint.sh"]
