FROM debian:stable-slim

# Install OpenVPN, Kerberos, Python, and other tools
RUN apt-get update && apt-get install -y \
    openvpn \
    easy-rsa \
    python3 \
    python3-venv \
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

# Set the working directory
WORKDIR /app

# Copy your application files
COPY . /app

# Set up virtual environment and install Python dependencies
RUN python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install \
        flask \
        python-dotenv \
        gssapi

# Make the venv available in PATH
ENV PATH="/venv/bin:$PATH"

# Copy entrypoint script and make it executable
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ⚠️ DO NOT DROP TO NON-ROOT USER — required to copy to /etc/krb5.keytab
# RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
# USER appuser

# Expose Flask UI and OpenVPN UDP port
EXPOSE 8080 1194/udp

# Run the entrypoint script
CMD ["/entrypoint.sh"]
