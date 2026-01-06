#!/bin/bash

# Test script for Game Session Allocation Service API
# Usage: ./test-api.sh <service-url>

set -e

SERVICE_URL="${1:-http://localhost:5000}"

echo "=== Testing Game Session Allocation Service ==="
echo "Service URL: ${SERVICE_URL}"
echo ""

# Test 1: Health check
echo "Test 1: Health Check"
curl -s "${SERVICE_URL}/health" | python3 -m json.tool
echo ""

# Test 2: Service info
echo "Test 2: Service Info"
curl -s "${SERVICE_URL}/" | python3 -m json.tool
echo ""

# Test 3: Create session
echo "Test 3: Create Session"
SESSION_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/api/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": "test-player-1",
    "game_mode": "battle-royale",
    "server_region": "us-east",
    "max_players": 4
  }')
echo "${SESSION_RESPONSE}" | python3 -m json.tool
SESSION_ID=$(echo "${SESSION_RESPONSE}" | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")
echo "Created Session ID: ${SESSION_ID}"
echo ""

# Test 4: Get session
echo "Test 4: Get Session"
curl -s "${SERVICE_URL}/api/sessions/${SESSION_ID}" | python3 -m json.tool
echo ""

# Test 5: List sessions
echo "Test 5: List Sessions"
curl -s "${SERVICE_URL}/api/sessions" | python3 -m json.tool
echo ""

# Test 6: Join session
echo "Test 6: Join Session"
curl -s -X POST "${SERVICE_URL}/api/sessions/${SESSION_ID}/join" \
  -H "Content-Type: application/json" \
  -d '{"player_id": "test-player-2"}' | python3 -m json.tool
echo ""

# Test 7: Get updated session
echo "Test 7: Get Updated Session (should show 2 players)"
curl -s "${SERVICE_URL}/api/sessions/${SESSION_ID}" | python3 -m json.tool
echo ""

# Test 8: List sessions with filter
echo "Test 8: List Active Sessions"
curl -s "${SERVICE_URL}/api/sessions?status=active" | python3 -m json.tool
echo ""

# Test 9: End session
echo "Test 9: End Session"
curl -s -X POST "${SERVICE_URL}/api/sessions/${SESSION_ID}/end" | python3 -m json.tool
echo ""

# Test 10: Verify session ended
echo "Test 10: Verify Session Ended (status should be 'completed')"
curl -s "${SERVICE_URL}/api/sessions/${SESSION_ID}" | python3 -m json.tool
echo ""

# Test 11: Create another session for deletion test
echo "Test 11: Create Another Session"
DELETE_SESSION_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/api/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": "test-player-3",
    "game_mode": "deathmatch",
    "server_region": "us-west",
    "max_players": 8
  }')
echo "${DELETE_SESSION_RESPONSE}" | python3 -m json.tool
DELETE_SESSION_ID=$(echo "${DELETE_SESSION_RESPONSE}" | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")
echo ""

# Test 12: Delete session
echo "Test 12: Delete Session"
curl -s -X DELETE "${SERVICE_URL}/api/sessions/${DELETE_SESSION_ID}" | python3 -m json.tool
echo ""

# Test 13: Verify deletion (should return 404)
echo "Test 13: Verify Deletion (should return 404)"
curl -s "${SERVICE_URL}/api/sessions/${DELETE_SESSION_ID}" | python3 -m json.tool
echo ""

echo "=== All Tests Completed ==="
