"""
Game Session Allocation Service - Main Application
A stateless REST API for managing game sessions with MySQL backend
"""

import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql-service'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'gameuser'),
    'password': os.getenv('DB_PASSWORD', 'gamepass'),
    'database': os.getenv('DB_NAME', 'gamedb')
}


def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        app.logger.error(f"Database connection error: {e}")
        raise


def init_db():
    """Initialize database schema"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                session_id VARCHAR(36) PRIMARY KEY,
                player_id VARCHAR(100) NOT NULL,
                game_mode VARCHAR(50) NOT NULL,
                server_region VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'active',
                max_players INT NOT NULL DEFAULT 4,
                current_players INT NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_player_id (player_id),
                INDEX idx_status (status)
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        app.logger.info("Database initialized successfully")
    except Error as e:
        app.logger.error(f"Database initialization error: {e}")
        raise


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes probes"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        connection.close()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503


@app.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check endpoint for Kubernetes"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM game_sessions")
        cursor.fetchone()
        cursor.close()
        connection.close()
        return jsonify({'status': 'ready'}), 200
    except Exception as e:
        return jsonify({'status': 'not ready', 'error': str(e)}), 503


@app.route('/api/sessions', methods=['POST'])
def create_session():
    """
    Create a new game session
    Request body: {
        "player_id": "string",
        "game_mode": "string",
        "server_region": "string",
        "max_players": int (optional, default 4)
    }
    """
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['player_id', 'game_mode', 'server_region']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        session_id = str(uuid.uuid4())
        player_id = data['player_id']
        game_mode = data['game_mode']
        server_region = data['server_region']
        max_players = data.get('max_players', 4)
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            INSERT INTO game_sessions 
            (session_id, player_id, game_mode, server_region, max_players, current_players, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (session_id, player_id, game_mode, server_region, max_players, 1, 'active'))
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'session_id': session_id,
            'player_id': player_id,
            'game_mode': game_mode,
            'server_region': server_region,
            'max_players': max_players,
            'current_players': 1,
            'status': 'active',
            'message': 'Session created successfully'
        }), 201
        
    except Exception as e:
        app.logger.error(f"Error creating session: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details by session_id"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM game_sessions WHERE session_id = %s"
        cursor.execute(query, (session_id,))
        session = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Convert datetime objects to strings
        session['created_at'] = session['created_at'].isoformat() if session['created_at'] else None
        session['updated_at'] = session['updated_at'].isoformat() if session['updated_at'] else None
        
        return jsonify(session), 200
        
    except Exception as e:
        app.logger.error(f"Error retrieving session: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """
    List all sessions with optional filters
    Query params: status, player_id, game_mode, server_region
    """
    try:
        status = request.args.get('status')
        player_id = request.args.get('player_id')
        game_mode = request.args.get('game_mode')
        server_region = request.args.get('server_region')
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM game_sessions WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = %s"
            params.append(status)
        if player_id:
            query += " AND player_id = %s"
            params.append(player_id)
        if game_mode:
            query += " AND game_mode = %s"
            params.append(game_mode)
        if server_region:
            query += " AND server_region = %s"
            params.append(server_region)
        
        query += " ORDER BY created_at DESC LIMIT 100"
        
        cursor.execute(query, params)
        sessions = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Convert datetime objects to strings
        for session in sessions:
            session['created_at'] = session['created_at'].isoformat() if session['created_at'] else None
            session['updated_at'] = session['updated_at'].isoformat() if session['updated_at'] else None
        
        return jsonify({'sessions': sessions, 'count': len(sessions)}), 200
        
    except Exception as e:
        app.logger.error(f"Error listing sessions: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/sessions/<session_id>/join', methods=['POST'])
def join_session(session_id):
    """
    Join an existing session
    Request body: {"player_id": "string"}
    """
    try:
        data = request.get_json()
        if not data or 'player_id' not in data:
            return jsonify({'error': 'Missing player_id'}), 400
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get current session
        cursor.execute("SELECT * FROM game_sessions WHERE session_id = %s", (session_id,))
        session = cursor.fetchone()
        
        if not session:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Session not found'}), 404
        
        if session['status'] != 'active':
            cursor.close()
            connection.close()
            return jsonify({'error': 'Session is not active'}), 400
        
        if session['current_players'] >= session['max_players']:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Session is full'}), 400
        
        # Update session
        cursor.execute(
            "UPDATE game_sessions SET current_players = current_players + 1 WHERE session_id = %s",
            (session_id,)
        )
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'session_id': session_id,
            'player_id': data['player_id'],
            'message': 'Joined session successfully'
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error joining session: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session by session_id"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if session exists
        cursor.execute("SELECT session_id FROM game_sessions WHERE session_id = %s", (session_id,))
        session = cursor.fetchone()
        
        if not session:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Session not found'}), 404
        
        # Delete session
        cursor.execute("DELETE FROM game_sessions WHERE session_id = %s", (session_id,))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return jsonify({'message': 'Session deleted successfully'}), 200
        
    except Exception as e:
        app.logger.error(f"Error deleting session: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/sessions/<session_id>/end', methods=['POST'])
def end_session(session_id):
    """End a session by marking it as completed"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if session exists
        cursor.execute("SELECT session_id FROM game_sessions WHERE session_id = %s", (session_id,))
        session = cursor.fetchone()
        
        if not session:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Session not found'}), 404
        
        # Update session status
        cursor.execute("UPDATE game_sessions SET status = 'completed' WHERE session_id = %s", (session_id,))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return jsonify({'message': 'Session ended successfully'}), 200
        
    except Exception as e:
        app.logger.error(f"Error ending session: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information"""
    return jsonify({
        'service': 'Game Session Allocation Service',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'ready': '/ready',
            'create_session': 'POST /api/sessions',
            'get_session': 'GET /api/sessions/<session_id>',
            'list_sessions': 'GET /api/sessions',
            'join_session': 'POST /api/sessions/<session_id>/join',
            'end_session': 'POST /api/sessions/<session_id>/end',
            'delete_session': 'DELETE /api/sessions/<session_id>'
        }
    }), 200


if __name__ == '__main__':
    # Initialize database on startup
    try:
        init_db()
    except Exception as e:
        app.logger.error(f"Failed to initialize database: {e}")
    
    # Run the application
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
