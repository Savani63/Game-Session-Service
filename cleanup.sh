#!/bin/bash

# Delete all Game Session Service resources from Kubernetes

set -e

echo "=== Deleting Game Session Allocation Service ==="

# Delete in reverse order
echo "Deleting HPA..."
kubectl delete -f k8s/hpa.yaml --ignore-not-found=true

echo "Deleting Game Session Service..."
kubectl delete -f k8s/service.yaml --ignore-not-found=true
kubectl delete -f k8s/deployment.yaml --ignore-not-found=true

echo "Deleting MySQL..."
kubectl delete -f k8s/mysql-service.yaml --ignore-not-found=true
kubectl delete -f k8s/mysql-deployment.yaml --ignore-not-found=true
kubectl delete -f k8s/mysql-pvc.yaml --ignore-not-found=true

echo "Deleting ConfigMap and Secret..."
kubectl delete -f k8s/secret.yaml --ignore-not-found=true
kubectl delete -f k8s/configmap.yaml --ignore-not-found=true

echo "Deleting namespace..."
kubectl delete -f k8s/namespace.yaml --ignore-not-found=true

echo ""
echo "=== Cleanup Complete ==="
