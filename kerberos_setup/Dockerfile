FROM python:3.11-slim

WORKDIR /kerberos

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    krb5-kdc \
    krb5-admin-server \
    krb5-config \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set up virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python dependencies inside the venv
RUN pip install --upgrade pip && pip install python-dotenv

# Copy app files
COPY config.py driver.py /kerberos/

VOLUME /var/lib/krb5kdc /etc/krb5kdc

CMD ["python", "/kerberos/driver.py"]
