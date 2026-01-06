# Game Session Service - Output Examples

This document shows real examples of the Game Session Allocation Service in action.

## Live API Demonstration

Below are actual outputs from running the service and making API calls:

---

### 1. Service Information
```bash
curl http://localhost:5000/
```

**Output:**
```json
{
    "endpoints": {
        "create_session": "POST /api/sessions",
        "delete_session": "DELETE /api/sessions/<session_id>",
        "end_session": "POST /api/sessions/<session_id>/end",
        "get_session": "GET /api/sessions/<session_id>",
        "health": "/health",
        "join_session": "POST /api/sessions/<session_id>/join",
        "list_sessions": "GET /api/sessions",
        "ready": "/ready"
    },
    "service": "Game Session Allocation Service",
    "version": "1.0.0"
}
```

---

### 2. Health Check
```bash
curl http://localhost:5000/health
```

**Output:**
```json
{
    "database": "connected",
    "status": "healthy"
}
```

---

### 3. Create Game Session (Battle Royale)
```bash
curl -X POST http://localhost:5000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": "alice",
    "game_mode": "battle-royale",
    "server_region": "us-east",
    "max_players": 4
  }'
```

**Output:**
```json
{
    "current_players": 1,
    "game_mode": "battle-royale",
    "max_players": 4,
    "message": "Session created successfully",
    "player_id": "alice",
    "server_region": "us-east",
    "session_id": "ae0c703a-e3f1-4327-b6c8-bfb487603ab2",
    "status": "active"
}
```

---

### 4. Create Another Session (Deathmatch)
```bash
curl -X POST http://localhost:5000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": "bob",
    "game_mode": "deathmatch",
    "server_region": "eu-west",
    "max_players": 8
  }'
```

**Output:**
```json
{
    "current_players": 1,
    "game_mode": "deathmatch",
    "max_players": 8,
    "message": "Session created successfully",
    "player_id": "bob",
    "server_region": "eu-west",
    "session_id": "0d537ea3-512b-49e1-b516-f54e8100dc75",
    "status": "active"
}
```

---

### 5. List All Sessions
```bash
curl http://localhost:5000/api/sessions
```

**Output:**
```json
{
    "count": 2,
    "sessions": [
        {
            "created_at": "2026-01-06T20:10:49",
            "current_players": 1,
            "game_mode": "deathmatch",
            "max_players": 8,
            "player_id": "bob",
            "server_region": "eu-west",
            "session_id": "0d537ea3-512b-49e1-b516-f54e8100dc75",
            "status": "active",
            "updated_at": "2026-01-06T20:10:49"
        },
        {
            "created_at": "2026-01-06T20:10:49",
            "current_players": 1,
            "game_mode": "battle-royale",
            "max_players": 4,
            "player_id": "alice",
            "server_region": "us-east",
            "session_id": "ae0c703a-e3f1-4327-b6c8-bfb487603ab2",
            "status": "active",
            "updated_at": "2026-01-06T20:10:49"
        }
    ]
}
```

---

### 6. Join a Session
```bash
curl -X POST http://localhost:5000/api/sessions/0d537ea3-512b-49e1-b516-f54e8100dc75/join \
  -H "Content-Type: application/json" \
  -d '{"player_id": "charlie"}'
```

**Output:**
```json
{
    "message": "Joined session successfully",
    "player_id": "charlie",
    "session_id": "0d537ea3-512b-49e1-b516-f54e8100dc75"
}
```

---

### 7. Get Specific Session (Now with 2 Players)
```bash
curl http://localhost:5000/api/sessions/0d537ea3-512b-49e1-b516-f54e8100dc75
```

**Output:**
```json
{
    "created_at": "2026-01-06T20:10:49",
    "current_players": 2,
    "game_mode": "deathmatch",
    "max_players": 8,
    "player_id": "bob",
    "server_region": "eu-west",
    "session_id": "0d537ea3-512b-49e1-b516-f54e8100dc75",
    "status": "active",
    "updated_at": "2026-01-06T20:10:49"
}
```

---

### 8. Filter Sessions by Game Mode
```bash
curl "http://localhost:5000/api/sessions?game_mode=deathmatch"
```

**Output:**
```json
{
    "count": 1,
    "sessions": [
        {
            "created_at": "2026-01-06T20:10:49",
            "current_players": 2,
            "game_mode": "deathmatch",
            "max_players": 8,
            "player_id": "bob",
            "server_region": "eu-west",
            "session_id": "0d537ea3-512b-49e1-b516-f54e8100dc75",
            "status": "active",
            "updated_at": "2026-01-06T20:10:49"
        }
    ]
}
```

---

### 9. End a Session
```bash
curl -X POST http://localhost:5000/api/sessions/0d537ea3-512b-49e1-b516-f54e8100dc75/end
```

**Output:**
```json
{
    "message": "Session ended successfully"
}
```

---

### 10. Verify Session Status Changed to Completed
```bash
curl http://localhost:5000/api/sessions/0d537ea3-512b-49e1-b516-f54e8100dc75
```

**Output:**
```json
{
    "created_at": "2026-01-06T20:10:49",
    "current_players": 2,
    "game_mode": "deathmatch",
    "max_players": 8,
    "player_id": "bob",
    "server_region": "eu-west",
    "session_id": "0d537ea3-512b-49e1-b516-f54e8100dc75",
    "status": "completed",
    "updated_at": "2026-01-06T20:10:49"
}
```

---

## How to See This Output Yourself

### Option 1: Quick Test with Docker Compose
```bash
# Start the service
docker-compose up

# In another terminal, run the test script
./test-api.sh http://localhost:5000
```

### Option 2: Local Python Development
```bash
# Start MySQL
docker run -d --name mysql-dev \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=gamedb \
  -e MYSQL_USER=gameuser \
  -e MYSQL_PASSWORD=gamepass \
  -p 3306:3306 \
  mysql:8.0

# Set environment variables
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=gameuser
export DB_PASSWORD=gamepass
export DB_NAME=gamedb

# Run the application
python app.py

# In another terminal, test the API
curl http://localhost:5000/
./test-api.sh http://localhost:5000
```

### Option 3: Kubernetes with Minikube
```bash
# Start Minikube
minikube start

# Build and deploy
eval $(minikube docker-env)
./build.sh
./deploy.sh

# Get service URL
SERVICE_URL=$(minikube service game-session-service -n game-session --url)

# Test the API
./test-api.sh $SERVICE_URL
```

---

## Using a Web Browser

You can also view some endpoints in your web browser:

1. **Service Info**: `http://localhost:5000/`
2. **Health Check**: `http://localhost:5000/health`
3. **List Sessions**: `http://localhost:5000/api/sessions`

For POST/DELETE operations, use tools like:
- **Postman** (https://www.postman.com/)
- **Insomnia** (https://insomnia.rest/)
- **curl** (command line)
- Browser extensions (RESTClient, Thunder Client, etc.)

---

## Kubernetes Pod Logs Example

When running in Kubernetes, you can view the application logs:

```bash
kubectl logs -f deployment/game-session-service -n game-session
```

**Example Output:**
```
[2026-01-06 20:10:45 +0000] [1] [INFO] Starting gunicorn 21.2.0
[2026-01-06 20:10:45 +0000] [1] [INFO] Listening at: http://0.0.0.0:5000 (1)
[2026-01-06 20:10:45 +0000] [1] [INFO] Using worker: sync
[2026-01-06 20:10:45 +0000] [7] [INFO] Booting worker with pid: 7
[2026-01-06 20:10:45 +0000] [8] [INFO] Booting worker with pid: 8
[2026-01-06 20:10:45 +0000] [9] [INFO] Booting worker with pid: 9
[2026-01-06 20:10:45 +0000] [10] [INFO] Booting worker with pid: 10
```

---

## Monitoring Auto-Scaling

To see the HorizontalPodAutoscaler in action:

```bash
# Watch the HPA status
kubectl get hpa -n game-session -w
```

**Example Output:**
```
NAME                 REFERENCE                       TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
game-session-hpa     Deployment/game-session-service 15%/70%, 20%/80%  3         10        3          5m
```

---

## Summary

This Game Session Allocation Service provides:
- ✅ RESTful API for session management
- ✅ Real-time session tracking with MySQL persistence
- ✅ Kubernetes auto-scaling (3-10 pods)
- ✅ Health checks and monitoring
- ✅ Load balancing across multiple instances
- ✅ Stateless design for horizontal scalability

For more information, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md).
