FROM alpine:3.19

# Set working directory
WORKDIR /app

# Environment variables
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install build tools and runtime dependencies
RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    py3-virtualenv \
    build-base \
    curl \
    wget \
    git \
    openssl-dev \
    pcre-dev \
    zlib-dev \
    supervisor \
    bash \
    nginx \
    ca-certificates \
    && ln -sf python3 /usr/bin/python && ln -sf pip3 /usr/bin/pip

# Build NGINX with RTMP module from source
RUN mkdir -p /usr/src/nginx && \
    cd /usr/src/nginx && \
    wget http://nginx.org/download/nginx-1.25.3.tar.gz && \
    tar -zxvf nginx-1.25.3.tar.gz && \
    git clone https://github.com/arut/nginx-rtmp-module.git && \
    cd nginx-1.25.3 && \
    ./configure --prefix=/usr/local/nginx \
                --with-http_ssl_module \
                --with-http_v2_module \
                --with-stream \
                --with-stream_ssl_module \
                --add-module=../nginx-rtmp-module && \
    make && make install

# Optional: Create SSL directory
RUN mkdir -p /etc/nginx/ssl

# Copy NGINX config and stat page
COPY ./system_files/nginx.conf /usr/local/nginx/conf/nginx.conf
COPY ./system_files/stat.xsl /usr/local/nginx/html/stat.xsl

# Copy Supervisor config
COPY ./system_files/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy Python dependencies and install them
COPY ./system_files/requirements.txt .
RUN python3 -m venv $VIRTUAL_ENV && \
    pip install --no-cache-dir -r requirements.txt

# Copy Flask app and support files
COPY api/ /app/api/
COPY config.py /app/
COPY driver.py /app/
COPY services/ /app/services/
COPY utils/ /app/utils/
COPY tests/ /app/tests/
COPY ./system_files/close_stream.sh /app/close_stream.sh
COPY ./system_files/entrypoint.sh /entrypoint.sh

# Set execution permissions
RUN chmod +x /app/close_stream.sh /entrypoint.sh

# Copy test folder (if any)
COPY tests/ /app/tests/

# Expose RTMP, Flask, and NGINX ports
EXPOSE 1935 5004 8080

# Use entrypoint to manage startup and tests
ENTRYPOINT ["/entrypoint.sh"]
