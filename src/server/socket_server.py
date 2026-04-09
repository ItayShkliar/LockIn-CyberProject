import socket
import json
import threading
import sqlite3
import hashlib
import os

# Import your existing logic just like Flask did
from database.db_manager import get_connection, init_db, create_initial_user_stats, get_user_stats, update_user_stats, get_user_sessions
from logic.stats_engine import StatsEngine 

HOST = '0.0.0.0'
PORT = 65432
DB_PATH = os.path.join(os.path.dirname(__file__), "database", "lockin.db")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def handle_client(conn, addr):
    try:
        data = conn.recv(8192)
        if not data:
            return
            
        # Parse the incoming JSON request
        request = json.loads(data.decode('utf-8'))
        action = request.get("action")
        response = {"status": "error", "message": "Unknown action"}

        db_conn = get_connection()
        cursor = db_conn.cursor()

        # ROUTE: REGISTER
        if action == "register":
            username = request.get('username')
            email = request.get('email')
            password = request.get('password')
            hashed_pw = hash_password(password)
            try:
                cursor.execute("INSERT INTO Users (username, email, password_hash) VALUES (?, ?, ?)", 
                               (username, email, hashed_pw))
                user_id = cursor.lastrowid
                db_conn.commit()
                create_initial_user_stats(user_id)
                response = {"status": "success", "user_id": user_id, "message": "User registered successfully"}
                print(f"[Server] Registered new user: {username}")
            except sqlite3.IntegrityError:
                response = {"status": "error", "message": "Username or email already exists"}

        # ROUTE: LOGIN
        elif action == "login":
            username = request.get('username')
            password = request.get('password')
            cursor.execute("SELECT user_id, password_hash FROM Users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if user and hash_password(password) == user[1]:
                user_id = user[0]
                cursor.execute("UPDATE Users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?", (user_id,))
                db_conn.commit()
                response = {"status": "success", "user_id": user_id, "message": "Login successful"}
                print(f"[Server] User logged in: {username}")
            else:
                response = {"status": "error", "message": "Invalid username or password"}

        # ROUTE: UPLOAD SESSION
        elif action == "upload_session":
            user_id = request.get('user_id')
            session_data = request.get('session_data')
            
            cursor.execute("""
                INSERT INTO Sessions (user_id, start_time, end_time, focus_time_seconds, distraction_count, description, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, session_data.get('start_time'), session_data.get('end_time'),
                session_data.get('focus_time_seconds', 0), session_data.get('distraction_count', 0), 
                session_data.get('description', 'Focus Session'), session_data.get('status', 'completed')
            ))
            
            focus_time = session_data.get('focus_time_seconds', 0)
            cursor.execute("""
                UPDATE CompetitionParticipants
                SET total_focus_time_seconds = total_focus_time_seconds + ?
                WHERE user_id = ? AND competition_id IN (
                    SELECT competition_id FROM Competitions WHERE status = 'active'
                )
            """, (focus_time, user_id))
            
            db_conn.commit()
            
            current_stats = get_user_stats(user_id)
            if current_stats:
                updated_stats = StatsEngine.calculate_updated_totals(current_stats, session_data)
                update_user_stats(user_id, updated_stats)
                
            response = {"status": "success", "message": "Session and stats updated successfully"}
            
        # ROUTE: GET SESSIONS
        elif action == "get_sessions":
            user_id = request.get("user_id")
            sessions = get_user_sessions(user_id)
            # convert datetime objects to strings if get_user_sessions detects types
            for s in sessions:
                s['start_time'] = str(s['start_time'])
                s['end_time'] = str(s['end_time'])
            response = {"status": "success", "sessions": sessions}
            
        # ROUTE: CREATE COMPETITION
        elif action == "create_competition":
            user_id = request.get("user_id")
            name = request.get("name")
            start_date = request.get("start_date")
            end_date = request.get("end_date")
            description = request.get("description")

            # 1. Create the room
            cursor.execute("""
                INSERT INTO Competitions (name, creator_id, start_date, end_date, description)
                VALUES (?, ?, ?, ?, ?)
            """, (name, user_id, start_date, end_date, description))
            room_code = cursor.lastrowid # This ID becomes the invite code
            
            # 2. Automatically add the creator as the first participant
            cursor.execute("""
                INSERT INTO CompetitionParticipants (competition_id, user_id)
                VALUES (?, ?)
            """, (room_code, user_id))
            
            db_conn.commit()
            response = {"status": "success", "room_code": room_code, "message": "Room created!"}

        # ROUTE: JOIN COMPETITION
        elif action == "join_competition":
            user_id = request.get("user_id")
            room_code = request.get("competition_id")

            try:
                cursor.execute("""
                    INSERT INTO CompetitionParticipants (competition_id, user_id)
                    VALUES (?, ?)
                """, (room_code, user_id))
                db_conn.commit()
                response = {"status": "success", "message": f"Successfully joined room {room_code}"}
            except sqlite3.IntegrityError:
                response = {"status": "error", "message": "You are already in this room or room doesn't exist."}

        # ROUTE: GET LEADERBOARD
        elif action == "get_leaderboard":
            room_code = request.get("competition_id")
            
            cursor.execute("""
                SELECT u.username, cp.total_focus_time_seconds, cp.rank
                FROM CompetitionParticipants cp
                JOIN Users u ON cp.user_id = u.user_id
                WHERE cp.competition_id = ?
                ORDER BY cp.total_focus_time_seconds DESC
            """, (room_code,))
            
            leaderboard = [{"username": row[0], "focus_time": row[1], "rank": row[2]} for row in cursor.fetchall()]
            response = {"status": "success", "leaderboard": leaderboard}

        # ---> NEW ROUTE: GET USER COMPETITIONS (This was missing!) <---
        elif action == "get_user_competitions":
            user_id = request.get("user_id")
            cursor.execute("""
                SELECT c.competition_id, c.name, c.description, c.start_date, c.end_date
                FROM Competitions c
                JOIN CompetitionParticipants cp ON c.competition_id = cp.competition_id
                WHERE cp.user_id = ?
                ORDER BY c.competition_id DESC
            """, (user_id,))
            
            # Use str() to cast datetime objects so JSON doesn't crash
            rooms = [
                {
                    "id": row[0], 
                    "name": row[1], 
                    "desc": row[2], 
                    "start": str(row[3]), 
                    "end": str(row[4])
                } 
                for row in cursor.fetchall()
            ]
            response = {"status": "success", "rooms": rooms}

        db_conn.close()
        
        # Send the response back to the client
        conn.sendall(json.dumps(response).encode('utf-8'))
        
    except Exception as e:
        print(f"[Server Error] {e}")
        error_response = {"status": "error", "message": str(e)}
        conn.sendall(json.dumps(error_response).encode('utf-8'))
    finally:
        conn.close()

def start_server():
    init_db()  
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    
    # NEW: Tell the server to wake up every 1 second
    server.settimeout(1.0) 
    
    server.listen(5)
    print(f"[Server] Raw socket server listening on {HOST}:{PORT}...")
    
    try:
        while True:
            try:
                conn, addr = server.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr))
                thread.start()
            except socket.timeout:
                # The 1 second passed with no connections. 
                # Python wakes up, silently passes, checks for Ctrl+C, and loops back to sleep.
                pass 
                
    except KeyboardInterrupt:
        print("\n[Server] Ctrl+C detected! Shutting down gracefully. Goodbye!")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()