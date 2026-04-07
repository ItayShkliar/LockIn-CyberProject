"""
Session API Routes
Handles all endpoints related to uploading and managing focus sessions.
"""
from flask import Blueprint, request, jsonify
import sqlite3
import os

from logic.stats_engine import StatsEngine # <-- IMPORT ENGINE
from database.db_manager import get_user_stats, update_user_stats # <-- IMPORT DB HELPERS

session_api = Blueprint('session_api', __name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "lockin.db")

@session_api.route('/api/session/upload', methods=['POST'])
def upload_session():
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'session_data' not in data:
        return jsonify({"status": "error", "message": "Missing user_id or session_data"}), 400
        
    user_id = data['user_id']
    session_data = data['session_data']
    
    try:
        # 1. Save the raw session to the Sessions table
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Sessions (
                user_id, start_time, end_time, focus_time_seconds, 
                distraction_count, description, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, session_data.get('start_time'), session_data.get('end_time'), 
            session_data.get('focus_time_seconds', 0), session_data.get('distraction_count', 0), 
            session_data.get('description', 'Focus Session'), session_data.get('status', 'completed')
        ))
        conn.commit()
        conn.close()
        
        # 2. Grab their current stats
        current_stats = get_user_stats(user_id)
        
        if current_stats:
            # 3. Ask the Engine to calculate the new totals
            updated_stats = StatsEngine.calculate_updated_totals(current_stats, session_data)
            
            # 4. Save the updated totals to the UserStats table
            update_user_stats(user_id, updated_stats)
            print(f"[API] Updated stats for User {user_id}. New Total Focus: {updated_stats['total_focus_time_seconds']}s")
            
        return jsonify({"status": "success", "message": "Session and stats updated successfully"}), 201
        
    except Exception as e:
        print(f"[API Error] Session upload failed: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500