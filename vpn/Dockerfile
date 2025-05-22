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

# Add the entrypoint script with universal execute permission
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

# Add app user and give permissions to their home
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser && \
    mkdir -p /home/appuser/.krb5 && chown -R appuser:appgroup /home/appuser

USER appuser

EXPOSE 8080 1194/udp

CMD ["/entrypoint.sh"]
