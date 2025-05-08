# Use Ubuntu as the base image
FROM ubuntu:20.04

# Install dependencies including Nginx and RTMP module
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    build-essential \
    libpcre3 \
    libpcre3-dev \
    zlib1g-dev \
    libssl-dev \
    wget \
    git

# Install Nginx with the RTMP module from source
RUN mkdir -p /usr/src/nginx \
    && cd /usr/src/nginx \
    && wget http://nginx.org/download/nginx-1.21.1.tar.gz \
    && tar -zxvf nginx-1.21.1.tar.gz \
    && git clone https://github.com/arut/nginx-rtmp-module.git \
    && cd nginx-1.21.1 \
    && ./configure --with-http_ssl_module --with-http_v2_module --with-stream --with-stream_ssl_module --with-compat --add-dynamic-module=../nginx-rtmp-module \
    && make \
    && make install

# Copy the custom Nginx configuration file (includes RTMP settings)
COPY nginx.conf /usr/local/nginx/conf

COPY close_stream.sh /app/close_stream.sh
RUN chmod +x /app/close_stream.sh


# Create a directory for SSL certificates (optional)
RUN mkdir -p /etc/nginx/ssl

# Work in the app directory for the Flask API
WORKDIR /app

# Install Flask API dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the Flask API app file
COPY app.py /app/app.py

COPY stat.xsl /usr/local/nginx/html/stat.xsl

# Expose RTMP and Flask API ports
EXPOSE 1935 5004 8080

# Start both Nginx (RTMP) and the Flask API
CMD /usr/src/nginx/nginx-1.21.1/objs/nginx -g 'daemon off;' & python3 /app/app.py
