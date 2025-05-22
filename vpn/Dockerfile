
FROM alpine:3.18

RUN apk add --no-cache openvpn easy-rsa python3 py3-pip bash curl nginx

WORKDIR /app

COPY . /app

RUN pip install flask python-dotenv

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080 1194/udp

CMD ["/entrypoint.sh"]
