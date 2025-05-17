# Use Alpine as the base image
FROM alpine:3.19

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install system dependencies
RUN apk update && apk add --no-cache \
    bash \
    build-base \
    gcc \
    python3 \
    py3-pip \
    py3-virtualenv \
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
    nodejs \
    npm

# Create www-data user if not present
RUN id -u www-data || adduser -S -G www-data www-data || true

# Set up Python virtualenv
RUN python3 -m venv $VIRTUAL_ENV

# Optional: SSL cert generation
RUN mkdir -p /etc/nginx/ssl /opt/mediamtx && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/self-signed.key \
    -out /etc/nginx/ssl/self-signed.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost" && \
    openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048

# Download MediaMTX
WORKDIR /opt/mediamtx
RUN wget --no-check-certificate https://github.com/bluenviron/mediamtx/releases/download/v1.9.1/mediamtx_v1.9.1_linux_amd64.tar.gz && \
    tar -xvf mediamtx_v1.9.1_linux_amd64.tar.gz && \
    chmod +x mediamtx

# Set working directory for app
WORKDIR /app

# Copy backend files
COPY api/ /app/api/
COPY config.py /app/
COPY driver.py /app/
COPY __init__.py /app/
COPY models/ /app/models/
COPY services/ /app/services/
COPY tests/ /app/tests/
COPY utils/ /app/utils/
COPY system/entrypoint.sh /entrypoint.sh
COPY system/requirements.txt /app/requirements.txt
COPY system/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY system/nginx.conf /etc/nginx/nginx.conf
COPY system /app/system

# Install Python requirements
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy Vite frontend (profile, dashboard, etc.)
COPY static/ /app/static/
RUN mkdir -p /app/static/apps

RUN cd /app/static/loading && \
    npm install --legacy-peer-deps && \
    npm run build && \
    mkdir -p /app/static/apps/loading && \
    rm -rf /app/static/apps/loading/* && \
    cp -r dist/. /app/static/apps/$app/; \
  done



WORKDIR /app

# Set permissions
RUN chmod +x /entrypoint.sh

# Expose ports
EXPOSE 80 443 5000 3000

# Entrypoint
ENTRYPOINT ["/entrypoint.sh"]