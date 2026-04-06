"""
User API Routes
Handles all endpoints related to user management (Register, Login, Profile).
"""
from flask import Blueprint, request, jsonify
import sqlite3
import os
import hashlib  

user_api = Blueprint('user_api', __name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "lockin.db")

def hash_password(password: str) -> str:
    """Hashes a password using pure SHA-256 as specified in the design doc."""
    # Convert the string to bytes, hash it, and return the hexadecimal string
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

@user_api.route('/api/user/register', methods=['POST'])
def register():
    """Endpoint to register a new user."""
    data = request.get_json()
    
    # 1. Validate Input
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
    username = data['username']
    email = data['email']
    password = data['password']
    
    # 2. Hash the password using our custom SHA-256 function
    hashed_pw = hash_password(password)
    
    # 3. Save to Database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Users (username, email, password_hash)
            VALUES (?, ?, ?)
        """, (username, email, hashed_pw))
        
        new_user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"[API] New user registered: {username} (ID: {new_user_id})")
        return jsonify({"status": "success", "user_id": new_user_id, "message": "User registered successfully"}), 201
        
    except sqlite3.IntegrityError as e:
        conn.close()
        error_msg = str(e).lower()
        if "username" in error_msg:
            return jsonify({"status": "error", "message": "Username already exists"}), 409
        elif "email" in error_msg:
            return jsonify({"status": "error", "message": "Email already registered"}), 409
        else:
            return jsonify({"status": "error", "message": "Database constraint error"}), 400
            
    except Exception as e:
        print(f"[API Error] Registration failed: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

@user_api.route('/api/user/login', methods=['POST'])
def login():
    """Endpoint to authenticate a user."""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"status": "error", "message": "Missing username or password"}), 400
        
    username = data['username']
    password = data['password']
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Fetch user from DB
        cursor.execute("SELECT user_id, password_hash FROM Users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        # 2. Hash the incoming password and compare it to the one saved in the database
        if user:
            user_id = user[0]
            saved_hash = user[1]
            
            if hash_password(password) == saved_hash:
                # Update last login time
                cursor.execute("UPDATE Users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?", (user_id,))
                conn.commit()
                conn.close()
                
                print(f"[API] User logged in: {username} (ID: {user_id})")
                return jsonify({"status": "success", "user_id": user_id, "message": "Login successful"}), 200
                
        # If we get here, either the user wasn't found OR the password didn't match
        conn.close()
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401
            
    except Exception as e:
        print(f"[API Error] Login failed: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500