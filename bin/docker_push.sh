#!/bin/bash
# docker_push.sh
# Usage: ./bin/docker_push.sh <version>
# Example: ./bin/docker_push.sh 1.0.0

# Check if version argument is provided
if [ -z "$1" ]; then
  echo "Error: Version number required"
  echo "Usage: $0 <version>"
  echo "Example: $0 1.0.0"
  exit 1
fi

VERSION="$1"

cd "$(dirname "$0")"/.. || exit

# Check if version tag already exists on Docker Hub
echo "Checking if version ${VERSION} already exists..."
if docker buildx imagetools inspect kevincrane/inkplate-dashboard-server:${VERSION} > /dev/null 2>&1; then
  echo ""
  echo "Error: Version ${VERSION} already exists on Docker Hub!"
  echo "Version tags are immutable and cannot be overwritten."
  echo "Please use a different version number."
  echo ""
  echo "Existing tag: https://hub.docker.com/r/kevincrane/inkplate-dashboard-server/tags?name=${VERSION}"
  exit 1
fi

echo "Version ${VERSION} is available"
echo ""

# Set up Docker Buildx (if not already done)
docker buildx create --name intel-arm-xcompiler --use
docker buildx inspect --bootstrap

echo "Building and pushing multi-platform image..."
echo "Version: $VERSION"
echo ""

# Build and push with both the version tag and latest tag
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t kevincrane/inkplate-dashboard-server:${VERSION} \
  -t kevincrane/inkplate-dashboard-server:latest \
  --push .

echo ""
echo "Deployment complete!"
echo "Version ${VERSION}: https://hub.docker.com/r/kevincrane/inkplate-dashboard-server/tags?name=${VERSION}"
echo "Latest: https://hub.docker.com/r/kevincrane/inkplate-dashboard-server/tags?name=latest"
