FROM alpine:3.19

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TZ=Etc/UTC

# Install dependencies
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
    && ln -sf python3 /usr/bin/python && \
    ln -sf pip3 /usr/bin/pip

# Install Node.js 20 and npm from community repo
RUN apk add --no-cache nodejs-current npm && \
    npm install -g npm@latest

# Install WebTorrent CLI globally
RUN npm install -g webtorrent-cli

# Install Python dependencies
RUN pip install --no-cache-dir flask requests

# Set working directory
WORKDIR /app

# Copy app files
COPY . /app/

# Expose Flask port
EXPOSE 5002

# Run the Flask app
CMD ["python3", "app.py"]
