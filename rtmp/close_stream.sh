#!/bin/bash

# Arguments passed by exec_publish_done
eth_address=$1
secret=$2

# Log the start of the script
echo "$(date) - Ending stream for ${eth_address}, secret: ${secret}" >> /var/log/nginx/rtmp_cleanup.log

# Check if the secret is empty and log it
if [ -z "${secret}" ]; then
    echo "$(date) - Warning: Secret is empty for ${eth_address}" >> /var/log/nginx/rtmp_cleanup.log
fi

# Make an HTTP request to the Flask API to handle the stream ending
curl -X POST "http://localhost:5004/on_publish_done?eth_address=${eth_address}&secret=${secret}" -H "Content-Type: application/json"

# Check if the curl command was successful
if [ $? -eq 0 ]; then
    echo "$(date) - Successfully called /on_publish_done for ${eth_address}" >> /var/log/nginx/rtmp_cleanup.log
else
    echo "$(date) - Failed to call /on_publish_done for ${eth_address}" >> /var/log/nginx/rtmp_cleanup.log
fi
