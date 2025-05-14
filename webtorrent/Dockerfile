FROM alpine:3.19

ENV PYTHONUNBUFFERED=1
ENV TZ=Etc/UTC
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install base packages
RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    py3-virtualenv \
    curl \
    ffmpeg \
    inotify-tools \
    bash \
    build-base \
    libstdc++ \
    tzdata \
    nodejs \
    npm \
    && ln -sf python3 /usr/bin/python && ln -sf pip3 /usr/bin/pip

# Install WebTorrent CLI
RUN npm install -g webtorrent-cli

# Create and activate Python virtual environment, then install requirements
WORKDIR /app
COPY ./system/requirements.txt .
RUN python3 -m venv $VIRTUAL_ENV && \
    $VIRTUAL_ENV/bin/pip install --no-cache-dir -r requirements.txt

# Copy rest of the app
COPY . /app/

# Add entrypoint script
COPY ./system/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5002

ENTRYPOINT ["/entrypoint.sh"]
