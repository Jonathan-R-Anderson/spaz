FROM debian:stable-slim

RUN apt-get update && apt-get install -y \
  krb5-kdc \
  krb5-admin-server \
  krb5-config \
  vim \
  && rm -rf /var/lib/apt/lists/*

ENV REALM=EXAMPLE.COM
ENV DOMAIN=vpn.localhost
ENV PRINCIPAL=HTTP/vpn.localhost@EXAMPLE.COM
ENV KEYTAB=/tmp/service.keytab

COPY krb5.conf.template /etc/krb5.conf
COPY create-principal.sh /root/create-principal.sh

RUN chmod +x /root/create-principal.sh

VOLUME /var/lib/krb5kdc /etc/krb5kdc

CMD ["/root/create-principal.sh"]
