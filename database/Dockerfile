FROM postgres:13

# Install additional dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    redis-server \
    netcat-traditional \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create and activate virtual environment
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python3 -m venv $VIRTUAL_ENV

# Copy requirements and install
COPY ./system/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy entrypoint script
COPY ./system/entrypoint.sh /docker-entrypoint-initdb.d/entrypoint.sh
RUN chmod +x /docker-entrypoint-initdb.d/entrypoint.sh
