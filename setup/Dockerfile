FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    krb5-kdc krb5-admin-server krb5-config \
    python3-venv && rm -rf /var/lib/apt/lists/*

# Set up Python environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY system/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application files
COPY . .

# Mount persistent volumes
VOLUME ["/var/lib/krb5kdc", "/etc/krb5kdc", "/kerberos/output"]

CMD ["python", "driver.py"]
