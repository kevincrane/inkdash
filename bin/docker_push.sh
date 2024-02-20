#!/bin/bash
# docker_push.sh

cd "$(dirname "$0")"/.. || exit

# Set up Docker Buildx (if not already done)
docker buildx create --name intel-arm-xcompiler --use
docker buildx inspect --bootstrap

echo "Pushing image to Docker Hub..."
docker buildx build --platform linux/amd64,linux/arm64 -t kevincrane/inkplate-dashboard-server:latest --push .
echo "Deployment complete, at: https://hub.docker.com/repository/docker/kevincrane/inkplate-dashboard-server"
