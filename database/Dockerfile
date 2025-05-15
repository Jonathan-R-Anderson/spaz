FROM postgres:13

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    redis-server netcat-traditional gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python3 -m venv $VIRTUAL_ENV

COPY ./system/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add init script to run after PostgreSQL initializes
COPY ./system/entrypoint.sh /docker-entrypoint-initdb.d/init-entrypoint.sh
RUN chmod +x /docker-entrypoint-initdb.d/init-entrypoint.sh
