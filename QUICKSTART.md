# Game Session Service - Quick Start Guide

This guide shows you how to quickly run and see the output of the Game Session Allocation Service.

## Option 1: Using Docker Compose (Easiest)

### Step 1: Start the Service

```bash
docker-compose up
```

You'll see output like:
```
Creating network "game-session-service_default" with the default driver
Creating volume "game-session-service_mysql_data" with default driver
Creating game-session-mysql ... done
Creating game-session-app   ... done
Attaching to game-session-mysql, game-session-app
game-session-mysql | [Server] /usr/sbin/mysqld: ready for connections.
game-session-app   | [INFO] Starting gunicorn 21.2.0
game-session-app   | [INFO] Listening at: http://0.0.0.0:5000
```

### Step 2: Access the Service

Open a new terminal and test the API:

```bash
# Get service information
curl http://localhost:5000/

# Create a game session
curl -X POST http://localhost:5000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": "player123",
    "game_mode": "battle-royale",
    "server_region": "us-east",
    "max_players": 4
  }'

# List all sessions
curl http://localhost:5000/api/sessions
```

### Step 3: Use the Test Script

```bash
./test-api.sh http://localhost:5000
```

This will run all API tests and show you the complete output.

### Step 4: Stop the Service

```bash
docker-compose down
```

---

## Option 2: Using Kubernetes (Minikube)

### Step 1: Start Minikube

```bash
minikube start
```

### Step 2: Build the Image

```bash
eval $(minikube docker-env)
./build.sh
```

### Step 3: Deploy the Service

```bash
./deploy.sh
```

You'll see:
```
=== Deploying Game Session Allocation Service ===
Creating namespace...
namespace/game-session created
Creating ConfigMap and Secret...
configmap/game-session-config created
secret/game-session-secret created
Deploying MySQL...
...
=== Deployment Complete ===
```

### Step 4: Check the Status

```bash
kubectl get all -n game-session
```

Output:
```
NAME                                        READY   STATUS    RESTARTS   AGE
pod/game-session-service-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
pod/game-session-service-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
pod/game-session-service-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
pod/mysql-xxxxxxxxxx-xxxxx                  1/1     Running   0          2m

NAME                           TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
service/game-session-service   LoadBalancer   10.96.xxx.xxx   <pending>     80:xxxxx/TCP   2m
service/mysql-service          ClusterIP      10.96.xxx.xxx   <none>        3306/TCP       2m
```

### Step 5: Access the Service

```bash
# Get the service URL
minikube service game-session-service -n game-session --url
```

This will output something like: `http://192.168.49.2:30123`

### Step 6: Test the API

```bash
# Use the URL from the previous step
SERVICE_URL=$(minikube service game-session-service -n game-session --url)

# Run tests
./test-api.sh $SERVICE_URL
```

### Step 7: View Logs

```bash
# View application logs
kubectl logs -f deployment/game-session-service -n game-session

# View MySQL logs
kubectl logs -f deployment/mysql -n game-session
```

### Step 8: Cleanup

```bash
./cleanup.sh
```

---

## Option 3: Local Python Development

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start MySQL

```bash
docker run -d --name mysql-dev \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=gamedb \
  -e MYSQL_USER=gameuser \
  -e MYSQL_PASSWORD=gamepass \
  -p 3306:3306 \
  mysql:8.0
```

### Step 3: Set Environment Variables

```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=gameuser
export DB_PASSWORD=gamepass
export DB_NAME=gamedb
export PORT=5000
```

### Step 4: Run the Application

```bash
python app.py
```

Output:
```
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://0.0.0.0:5000
Press CTRL+C to quit
```

### Step 5: Test in Another Terminal

```bash
./test-api.sh http://localhost:5000
```

### Step 6: Stop

Press `CTRL+C` in the terminal running the app, then:

```bash
docker rm -f mysql-dev
```

---

## Expected Output Examples

### Creating a Session

**Request:**
```bash
curl -X POST http://localhost:5000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": "player123",
    "game_mode": "battle-royale",
    "server_region": "us-east",
    "max_players": 4
  }'
```

**Response:**
```json
{
  "session_id": "d116be68-dfc5-4224-84c7-acb520f7379a",
  "player_id": "player123",
  "game_mode": "battle-royale",
  "server_region": "us-east",
  "max_players": 4,
  "current_players": 1,
  "status": "active",
  "message": "Session created successfully"
}
```

### Listing Sessions

**Request:**
```bash
curl http://localhost:5000/api/sessions
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "d116be68-dfc5-4224-84c7-acb520f7379a",
      "player_id": "player123",
      "game_mode": "battle-royale",
      "server_region": "us-east",
      "status": "active",
      "max_players": 4,
      "current_players": 1,
      "created_at": "2026-01-06T20:06:22",
      "updated_at": "2026-01-06T20:06:22"
    }
  ],
  "count": 1
}
```

### Joining a Session

**Request:**
```bash
curl -X POST http://localhost:5000/api/sessions/d116be68-dfc5-4224-84c7-acb520f7379a/join \
  -H "Content-Type: application/json" \
  -d '{"player_id": "player456"}'
```

**Response:**
```json
{
  "session_id": "d116be68-dfc5-4224-84c7-acb520f7379a",
  "player_id": "player456",
  "message": "Joined session successfully"
}
```

---

## Web Browser Access

You can also use your web browser to see some outputs:

1. **Service Info**: Navigate to `http://localhost:5000/` (or your service URL)
2. **Health Check**: Navigate to `http://localhost:5000/health`
3. **List Sessions**: Navigate to `http://localhost:5000/api/sessions`

For POST/DELETE requests, you'll need to use tools like:
- **Postman**: https://www.postman.com/
- **Insomnia**: https://insomnia.rest/
- **curl** (command line)
- **Browser extensions**: RESTClient, Advanced REST Client

---

## Troubleshooting

### Can't Access the Service

**Docker Compose:**
- Check if containers are running: `docker-compose ps`
- Check logs: `docker-compose logs -f`

**Kubernetes:**
- Check pod status: `kubectl get pods -n game-session`
- Check logs: `kubectl logs -f deployment/game-session-service -n game-session`

### Database Connection Errors

**Check MySQL is running:**
```bash
# Docker Compose
docker-compose ps mysql

# Kubernetes
kubectl get pods -n game-session -l app=mysql
```

**Check MySQL logs:**
```bash
# Docker Compose
docker-compose logs mysql

# Kubernetes
kubectl logs deployment/mysql -n game-session
```

---

## Quick Command Reference

| Action | Command |
|--------|---------|
| Start (Docker Compose) | `docker-compose up` |
| Stop (Docker Compose) | `docker-compose down` |
| Deploy (Kubernetes) | `./deploy.sh` |
| Cleanup (Kubernetes) | `./cleanup.sh` |
| Test API | `./test-api.sh <url>` |
| View logs (K8s) | `kubectl logs -f deployment/game-session-service -n game-session` |
| Get service URL (Minikube) | `minikube service game-session-service -n game-session --url` |
