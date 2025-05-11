FROM alpine:3.19

ENV PYTHONUNBUFFERED=1
ENV TZ=Etc/UTC

RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    ffmpeg \
    inotify-tools \
    bash \
    build-base \
    libstdc++ \
    tzdata \
    nodejs \
    npm \
    && ln -sf python3 /usr/bin/python && \
    ln -sf pip3 /usr/bin/pip

RUN npm install -g webtorrent-cli

WORKDIR /app

COPY ./system_files/requirements.txt .
RUN python3 -m venv $VIRTUAL_ENV && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 5002

CMD ["python3", "app.py"]
