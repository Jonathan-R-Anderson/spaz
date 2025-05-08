# Use Ubuntu as the base image
FROM ubuntu:20.04

# Set environment variables to make the installation non-interactive
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install system dependencies, Python, Jupyter, and Node.js
RUN apt-get update && apt-get install -y \
    bash \
    build-essential \
    gcc \
    python3 \
    python3-pip \
    libffi-dev \
    libssl-dev \
    ffmpeg \
    net-tools \
    supervisor \
    procps \
    openssl \
    tzdata \
    nginx \
    libnginx-mod-rtmp \
    openssl \
    curl \
    build-essential \
    git \
    bash \
    wget \
    ca-certificates \
    --no-install-recommends && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip && \
    rm -rf /var/lib/apt/lists/*

#RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
#    apt-get install -y nodejs


# Create a directory for SSL certificates
RUN mkdir -p /etc/nginx/ssl

# Generate a self-signed SSL certificate (valid for 365 days)
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/self-signed.key \
    -out /etc/nginx/ssl/self-signed.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"


# Generate a Diffie-Hellman group for added security
RUN openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048

# Download Mediamtx with SSL certificate validation disabled
RUN mkdir -p /opt/mediamtx && \
    cd /opt/mediamtx && \
    wget --no-check-certificate https://github.com/bluenviron/mediamtx/releases/download/v1.9.1/mediamtx_v1.9.1_linux_amd64.tar.gz && \
    tar -xvf mediamtx_v1.9.1_linux_amd64.tar.gz && \
    chmod +x mediamtx


# Copy the application code to the container
COPY . /app

# Set the working directory in the container
WORKDIR /app

# Install any Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the custom Nginx configuration file to the container
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports for HTTP (80), HTTPS (443)
EXPOSE 80 443 5000 3000
