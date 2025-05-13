# Use Alpine as the base image
FROM alpine:3.19

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

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
    && ln -sf python3 /usr/bin/python && \
    ln -sf pip3 /usr/bin/pip

RUN python3 -m venv $VIRTUAL_ENV

RUN mkdir -p /etc/nginx/ssl /opt/mediamtx

RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/self-signed.key \
    -out /etc/nginx/ssl/self-signed.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"

RUN openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048

WORKDIR /opt/mediamtx
RUN wget --no-check-certificate https://github.com/bluenviron/mediamtx/releases/download/v1.9.1/mediamtx_v1.9.1_linux_amd64.tar.gz && \
    tar -xvf mediamtx_v1.9.1_linux_amd64.tar.gz && \
    chmod +x mediamtx

WORKDIR /app
COPY . /app
COPY ./system/supervisord.conf .
COPY ./system/requirements.txt .
COPY ./system/nginx.conf /etc/nginx/nginx.conf
COPY ./system/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80 443 5000 3000

ENTRYPOINT ["/entrypoint.sh"]
