FROM debian:stable-slim

RUN apt-get update && apt-get install -y \
  krb5-kdc \
  krb5-admin-server \
  krb5-config \
  vim \
  python3 \
  python3-pip \
  && rm -rf /var/lib/apt/lists/*

RUN pip install python-dotenv


ENV KEYTAB=/tmp/service.keytab

# Create app directory
WORKDIR /kerberos



# Volumes for persistent state and output
VOLUME /var/lib/krb5kdc /etc/krb5kdc

COPY config.py /kerberos/
COPY driver.py /kerberos/

CMD ["python3", "/kerberos/driver.py"]
