FROM alpine:3.18

# Install core packages
RUN apk add --no-cache \
    openvpn \
    easy-rsa \
    python3 \
    py3-pip \
    bash \
    curl \
    krb5 \
    krb5-server \
    krb5-libs \
    krb5-extra \
    gssproxy \
    nginx \
    build-base \
    git

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

# Add krb5.conf and keytab files (should be mounted or copied securely)
# Example (commented, handled at runtime via volume):
# COPY ./krb5.conf /etc/krb5.conf
# COPY ./service.keytab /etc/krb5.keytab

# Create non-root user for better security (optional)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Expose HTTP and VPN ports
EXPOSE 8080 1194/udp

# Default command
CMD ["/entrypoint.sh"]
