# Use Alpine as the base image
FROM alpine:3.19

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install system dependencies
RUN apk update && apk add --no-cache \
    bash \
    build-base \
    gcc \
    python3 \
    py3-pip \
    libffi-dev \
    openssl \
    openssl-dev \
    ffmpeg \
    net-tools \
    supervisor \
    procps \
    tzdata \
    nginx \
    curl \
    git \
    wget \
    ca-certificates \
    && ln -sf python3 /usr/bin/python && \
    ln -sf pip3 /usr/bin/pip

# Create directories
RUN mkdir -p /etc/nginx/ssl /opt/mediamtx

# Generate a self-signed SSL certificate
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/self-signed.key \
    -out /etc/nginx/ssl/self-signed.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"

# Generate Diffie-Hellman parameters
RUN openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048

# Download Mediamtx (skip cert check since Alpine often lacks CA bundle in some contexts)
WORKDIR /opt/mediamtx
RUN wget --no-check-certificate https://github.com/bluenviron/mediamtx/releases/download/v1.9.1/mediamtx_v1.9.1_linux_amd64.tar.gz && \
    tar -xvf mediamtx_v1.9.1_linux_amd64.tar.gz && \
    chmod +x mediamtx

# Copy your application code
COPY . /app

# Set working directory
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir -r ./system_files/requirements.txt

# Replace default nginx config
COPY ./system_files/nginx.conf /etc/nginx/nginx.conf

# Expose needed ports
EXPOSE 80 443 5000 3000

# Default command (adjust as needed)
CMD ["supervisord", "-c", "/app/system_files/supervisord.conf"]
