FROM python:3.11-slim

WORKDIR /kerberos

# Install required system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    krb5-kdc \
    krb5-admin-server \
    krb5-config \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set up Python virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --upgrade pip && pip install python-dotenv

# Copy Python scripts
COPY driver.py config.py .env /kerberos/

# Mount persistent KDC storage
VOLUME ["/var/lib/krb5kdc", "/etc/krb5kdc", "/kerberos/output"]

CMD ["python", "/kerberos/driver.py"]
