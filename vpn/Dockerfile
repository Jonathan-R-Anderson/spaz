FROM debian:stable-slim

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

WORKDIR /app

COPY . /app

RUN python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install \
        flask \
        python-dotenv \
        gssapi

ENV PATH="/venv/bin:$PATH"

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8080 1194/udp

CMD ["/entrypoint.sh"]
