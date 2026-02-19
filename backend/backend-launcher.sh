#!/bin/bash 

# sudo docker-compose up --build

# Check if the camera device exists and ENABLE_CAMERA is true
if [ "$ENABLE_CAMERA" = "true" ] && [ -e /dev/video0 ]; then
    echo "Camera device found. Starting container with camera support."
    docker-compose -f docker-compose.yml run --service-ports --device /dev/video0:/dev/video0 app
else
    echo "Camera device not found or ENABLE_CAMERA is false. Starting container without camera support."
    docker-compose up -d
fi
