#!/bin/bash

# Deploy Game Session Service to Kubernetes
# This script deploys all Kubernetes resources in order

set -e

echo "=== Deploying Game Session Allocation Service ==="

# Create namespace
echo "Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# Create ConfigMap and Secret
echo "Creating ConfigMap and Secret..."
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Deploy MySQL
echo "Deploying MySQL..."
kubectl apply -f k8s/mysql-pvc.yaml
kubectl apply -f k8s/mysql-deployment.yaml
kubectl apply -f k8s/mysql-service.yaml

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/mysql -n game-session

# Deploy Game Session Service
echo "Deploying Game Session Service..."
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Wait for deployment to be ready
echo "Waiting for Game Session Service to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/game-session-service -n game-session

# Deploy HPA
echo "Deploying Horizontal Pod Autoscaler..."
kubectl apply -f k8s/hpa.yaml

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "To check the status:"
echo "  kubectl get all -n game-session"
echo ""
echo "To get the service URL:"
echo "  kubectl get service game-session-service -n game-session"
echo ""
echo "To view logs:"
echo "  kubectl logs -f deployment/game-session-service -n game-session"
