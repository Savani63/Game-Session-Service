#!/bin/bash

# Build Docker image for Game Session Service

set -e

IMAGE_NAME="game-session-service"
IMAGE_TAG="${1:-latest}"
FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

echo "=== Building Docker Image ==="
echo "Image: ${FULL_IMAGE}"
echo ""

docker build -t ${FULL_IMAGE} .

echo ""
echo "=== Build Complete ==="
echo "Image: ${FULL_IMAGE}"
echo ""
echo "To push to a registry:"
echo "  docker tag ${FULL_IMAGE} <registry>/${FULL_IMAGE}"
echo "  docker push <registry>/${FULL_IMAGE}"
echo ""
echo "For Minikube:"
echo "  eval \$(minikube docker-env)"
echo "  docker build -t ${FULL_IMAGE} ."
