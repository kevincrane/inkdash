#!/bin/bash
# docker_run.sh

LOCAL_PORT=10465
FLASK_PORT=5000

cd "$(dirname "$0")"/.. || exit
echo "Stopping existing container..."
docker-compose down

echo "Running Docker container..."
docker-compose up -d
#docker run -p ${LOCAL_PORT}:${FLASK_PORT} --name inkplate-dashboard-server --detach inkplate-dashboard-server

echo "Container is running on http://0.0.0.0:${LOCAL_PORT}"
