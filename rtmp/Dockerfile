FROM alpine:3.19

# Set working directory
WORKDIR /app

# Install build tools and runtime dependencies
RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    build-base \
    curl \
    wget \
    git \
    openssl-dev \
    pcre-dev \
    zlib-dev \
    supervisor \
    bash \
    libexecinfo-dev \
    nginx \
    && ln -sf python3 /usr/bin/python && ln -sf pip3 /usr/bin/pip

# Build NGINX with RTMP module from source
RUN mkdir -p /usr/src/nginx && \
    cd /usr/src/nginx && \
    wget http://nginx.org/download/nginx-1.21.1.tar.gz && \
    tar -zxvf nginx-1.21.1.tar.gz && \
    git clone https://github.com/arut/nginx-rtmp-module.git && \
    cd nginx-1.21.1 && \
    ./configure --prefix=/usr/local/nginx \
                --with-http_ssl_module \
                --with-http_v2_module \
                --with-stream \
                --with-stream_ssl_module \
                --add-module=../nginx-rtmp-module && \
    make && make install

# Copy your NGINX config and assets
COPY ./system_files/nginx.conf /usr/local/nginx/conf/nginx.conf
COPY ./system_files/stat.xsl /usr/local/nginx/html/stat.xsl

# Supervisor config
COPY ./system_files/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Flask API
COPY ./system_files/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py

# Close stream script
COPY ./system_files/close_stream.sh /app/close_stream.sh
RUN chmod +x /app/close_stream.sh

# Optional: SSL directory
RUN mkdir -p /etc/nginx/ssl

# Expose RTMP, HTTP, and Flask API ports
EXPOSE 1935 5004 8080

# Run Supervisor to manage NGINX and Flask
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
