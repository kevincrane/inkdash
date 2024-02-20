#!/bin/bash
# docker_build.sh

echo "Building Docker image..."
cd "$(dirname "$0")"/.. || exit
docker build -t inkplate-dashboard-server .
echo "Build complete."
