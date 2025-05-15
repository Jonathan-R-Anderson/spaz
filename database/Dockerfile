FROM postgres:13

# Install extras
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv redis-server \
    gcc libpq-dev netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python3 -m venv $VIRTUAL_ENV

COPY ./system/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY ./system/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Override CMD but keep default entrypoint
CMD ["/entrypoint.sh"]
