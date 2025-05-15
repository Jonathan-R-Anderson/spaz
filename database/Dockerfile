FROM postgres:13

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    redis-server netcat-traditional gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up Python venv
WORKDIR /app
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python3 -m venv $VIRTUAL_ENV
COPY ./system/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your full app
COPY . .

# ✅ Put your script here so the official entrypoint will run it during DB init
COPY ./system/entrypoint.sh /docker-entrypoint-initdb.d/init-app.sh
RUN chmod +x /docker-entrypoint-initdb.d/init-app.sh

# Optionally copy a custom postgresql.conf
COPY ./system/postgresql.conf /app/postgresql.conf
