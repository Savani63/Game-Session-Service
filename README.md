# Game Session Allocation Service

A Kubernetes-deployed, stateless Python REST service that simulates game session allocation for multiplayer systems. Designed for scalability and fault tolerance, it demonstrates distributed backend design, automated provisioning, failure recovery, and horizontal pod scaling using Kubernetes.

## Architecture

- **Application**: Flask-based REST API (Python 3.11)
- **Database**: MySQL 8.0 with persistent storage
- **Container**: Docker with multi-stage build and security best practices
- **Orchestration**: Kubernetes with auto-scaling, health checks, and load balancing

## Features

✅ **Stateless Design**: All session state stored in MySQL, enabling horizontal scaling  
✅ **Auto-Scaling**: HorizontalPodAutoscaler based on CPU/memory utilization  
✅ **Health Checks**: Liveness and readiness probes for reliability  
✅ **High Availability**: Multiple replicas with load balancing  
✅ **Resource Management**: CPU and memory limits/requests defined  
✅ **Security**: Non-root containers, secrets management, environment-based configuration  
✅ **Fault Tolerance**: Init containers ensure database availability before startup  

## API Endpoints

### Core Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Service information and API documentation |
| `GET` | `/health` | Health check endpoint (for liveness probe) |
| `GET` | `/ready` | Readiness check endpoint |
| `POST` | `/api/sessions` | Create a new game session |
| `GET` | `/api/sessions` | List all sessions (with optional filters) |
| `GET` | `/api/sessions/<id>` | Get specific session details |
| `POST` | `/api/sessions/<id>/join` | Join an existing session |
| `POST` | `/api/sessions/<id>/end` | End a session (mark as completed) |
| `DELETE` | `/api/sessions/<id>` | Delete a session |

### API Examples

#### Create Session
```bash
curl -X POST http://<service-url>/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": "player123",
    "game_mode": "battle-royale",
    "server_region": "us-east",
    "max_players": 4
  }'
```

#### List Sessions
```bash
curl http://<service-url>/api/sessions?status=active&game_mode=battle-royale
```

#### Join Session
```bash
curl -X POST http://<service-url>/api/sessions/<session-id>/join \
  -H "Content-Type: application/json" \
  -d '{"player_id": "player456"}'
```

## Prerequisites

- Docker
- Kubernetes cluster (Minikube, GKE, EKS, AKS, or similar)
- kubectl CLI configured

## Quick Start

### 1. Build the Docker Image

```bash
# Build the image
./build.sh

# For Minikube, use the Minikube Docker daemon
eval $(minikube docker-env)
./build.sh
```

### 2. Deploy to Kubernetes

```bash
# Deploy all resources
./deploy.sh

# Check deployment status
kubectl get all -n game-session

# Get the service URL
kubectl get service game-session-service -n game-session
```

### 3. Access the Service

```bash
# For Minikube
minikube service game-session-service -n game-session

# For cloud providers (LoadBalancer)
kubectl get service game-session-service -n game-session
# Use the EXTERNAL-IP shown
```

### 4. Test the API

```bash
# Get service info
curl http://<service-url>/

# Create a session
curl -X POST http://<service-url>/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"player_id": "player1", "game_mode": "deathmatch", "server_region": "us-west"}'

# List sessions
curl http://<service-url>/api/sessions
```

## Kubernetes Resources

The service deploys the following Kubernetes resources:

- **Namespace**: `game-session` - Isolated namespace for all resources
- **ConfigMap**: Configuration for database connection and app settings
- **Secret**: Sensitive data (database passwords)
- **PersistentVolumeClaim**: 5Gi storage for MySQL data
- **MySQL Deployment**: Single replica with persistent storage
- **MySQL Service**: ClusterIP service for internal database access
- **App Deployment**: 3 replicas with rolling updates
- **App Service**: LoadBalancer for external access
- **HorizontalPodAutoscaler**: Auto-scales between 3-10 pods based on CPU/memory

## Scaling Behavior

The HPA automatically scales the application based on:

- **CPU**: Scales up when average utilization exceeds 70%
- **Memory**: Scales up when average utilization exceeds 80%
- **Min Replicas**: 3 (for high availability)
- **Max Replicas**: 10 (to handle traffic spikes)

Scale-up: Fast (0s stabilization, 100% increase per 30s)  
Scale-down: Conservative (300s stabilization, 50% decrease per 60s)

## Configuration

### Environment Variables

Configure via `k8s/configmap.yaml` and `k8s/secret.yaml`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `mysql-service` | MySQL hostname |
| `DB_PORT` | `3306` | MySQL port |
| `DB_NAME` | `gamedb` | Database name |
| `DB_USER` | `gameuser` | Database user |
| `DB_PASSWORD` | - | Database password (in Secret) |
| `PORT` | `5000` | Application port |

## Monitoring

### View Logs

```bash
# Application logs
kubectl logs -f deployment/game-session-service -n game-session

# MySQL logs
kubectl logs -f deployment/mysql -n game-session

# Specific pod logs
kubectl logs -f <pod-name> -n game-session
```

### Check Pod Status

```bash
# All resources
kubectl get all -n game-session

# Pod details
kubectl describe pod <pod-name> -n game-session

# HPA status
kubectl get hpa -n game-session
```

### Resource Usage

```bash
# Pod resource usage
kubectl top pods -n game-session

# Node resource usage
kubectl top nodes
```

## Cleanup

To remove all deployed resources:

```bash
./cleanup.sh
```

Or manually:

```bash
kubectl delete namespace game-session
```

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=gameuser
export DB_PASSWORD=gamepass
export DB_NAME=gamedb

# Run MySQL locally (Docker)
docker run -d \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=gamedb \
  -e MYSQL_USER=gameuser \
  -e MYSQL_PASSWORD=gamepass \
  -p 3306:3306 \
  mysql:8.0

# Run the application
python app.py
```

### Running Tests

```bash
# The application includes health and readiness endpoints for testing
curl http://localhost:5000/health
curl http://localhost:5000/ready
```

## Production Considerations

1. **Image Registry**: Push Docker image to a container registry (Docker Hub, ECR, GCR, ACR)
2. **Ingress**: Add Ingress controller for domain-based routing and TLS
3. **Monitoring**: Integrate with Prometheus/Grafana for metrics
4. **Logging**: Use ELK/EFK stack or cloud-native logging
5. **Database**: Use managed database service (RDS, Cloud SQL) for production
6. **Secrets**: Use external secret management (Vault, AWS Secrets Manager)
7. **CI/CD**: Implement automated build and deployment pipelines
8. **Resource Limits**: Tune based on actual load patterns
9. **Network Policies**: Add network policies for enhanced security
10. **Backup**: Implement database backup and disaster recovery

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n game-session

# Check pod events
kubectl describe pod <pod-name> -n game-session

# Check logs
kubectl logs <pod-name> -n game-session
```

### Database Connection Issues

```bash
# Verify MySQL is running
kubectl get pods -n game-session -l app=mysql

# Check MySQL logs
kubectl logs deployment/mysql -n game-session

# Test connection from app pod
kubectl exec -it deployment/game-session-service -n game-session -- \
  nc -zv mysql-service 3306
```

### Service Not Accessible

```bash
# Check service
kubectl get service game-session-service -n game-session

# For Minikube
minikube service list

# Check endpoints
kubectl get endpoints game-session-service -n game-session
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
