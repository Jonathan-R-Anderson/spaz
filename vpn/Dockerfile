FROM debian:stable-slim

# Install core system packages
RUN apt-get update && apt-get install -y \
    openvpn \
    easy-rsa \
    python3 \
    python3-pip \
    bash \
    curl \
    krb5-user \
    krb5-kdc \
    krb5-admin-server \
    libkrb5-dev \
    nginx \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application code
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    flask \
    python-dotenv \
    gssapi

# Copy entrypoint and make executable
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create non-root user for better security (optional)
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

# Expose HTTP and VPN ports
EXPOSE 8080 1194/udp

# Default command
CMD ["/entrypoint.sh"]
