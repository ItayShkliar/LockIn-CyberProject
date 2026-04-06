"""
Session API Routes
Handles all endpoints related to uploading and managing focus sessions.
"""
from flask import Blueprint, request, jsonify
import sqlite3
import os

session_api = Blueprint('session_api', __name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "lockin.db")

@session_api.route('/api/session/upload', methods=['POST'])
def upload_session():
    """Endpoint to upload a completed focus session."""
    data = request.get_json()
    
    # 1. Validate Input (Based on Design Document requirements)
    if not data or 'user_id' not in data or 'session_data' not in data:
        return jsonify({"status": "error", "message": "Missing user_id or session_data"}), 400
        
    user_id = data['user_id']
    session_data = data['session_data']
    
    # Extract session fields
    start_time = session_data.get('start_time')
    end_time = session_data.get('end_time')
    focus_time_seconds = session_data.get('focus_time_seconds', 0)
    distraction_count = session_data.get('distraction_count', 0)
    description = session_data.get('description', 'Focus Session')
    status = session_data.get('status', 'completed')
    
    if not start_time or not end_time:
        return jsonify({"status": "error", "message": "Missing start_time or end_time"}), 400
        
    # 2. Save to Database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Sessions (
                user_id, start_time, end_time, focus_time_seconds, 
                distraction_count, description, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, start_time, end_time, focus_time_seconds, 
            distraction_count, description, status
        ))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"[API] Session {session_id} saved for User {user_id}. Focus Time: {focus_time_seconds}s")
        return jsonify({
            "status": "success", 
            "session_id": session_id, 
            "message": "Session uploaded successfully"
        }), 201
        
    except sqlite3.IntegrityError:
        # This triggers if the user_id doesn't exist in the Users table (Foreign Key constraint)
        conn.close()
        return jsonify({"status": "error", "message": "Invalid user_id"}), 400
        
    except Exception as e:
        print(f"[API Error] Session upload failed: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500