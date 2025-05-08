FROM ubuntu:20.04

# Set environment variables to make the installation non-interactive
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    curl \
    inotify-tools \
    python3 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18.x and npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest

# Install WebTorrent CLI globally
RUN npm install -g webtorrent-cli

# Install Flask and required Python packages
RUN pip3 install flask requests

# Create the working directory
WORKDIR /app

# Copy the Flask app and the script to the container
COPY . /app/
# Expose the port that Flask will run on
EXPOSE 5002


# Use the startup script as the entry point
CMD ["python3", "app.py"]
