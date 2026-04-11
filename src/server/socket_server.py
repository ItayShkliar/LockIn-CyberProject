"""
LockIn TCP Socket Server (v2)
=================================
Handles all client communication over raw TCP sockets.
Uses a 4-byte length-prefixed framing protocol to prevent message fragmentation.

Protocol:
  - Every message is prefixed with a 4-byte big-endian integer indicating
    the byte length of the JSON payload that follows.
  - Client sends: [4-byte length][JSON bytes]
  - Server replies: [4-byte length][JSON bytes]

Routes (action field in JSON):
  register, login, upload_session, get_sessions,
  create_competition, join_competition, leave_competition,
  get_leaderboard, get_user_competitions, get_competition_details,
  get_public_competitions, get_global_leaderboard,
  get_user_profile, get_achievements
"""

import socket
import json
import struct
import threading
import sqlite3
import hashlib
import os
from datetime import datetime

from database.db_manager import (
    get_connection, init_db,
    create_initial_user_stats, get_user_stats, update_user_stats,
    get_user_sessions, get_user_profile,
    get_global_leaderboard,
    get_competition_details, get_public_competitions,
    recalculate_competition_ranks, update_competition_statuses,
    check_and_grant_achievements, get_user_achievements,
)
from logic.stats_engine import StatsEngine

HOST = '0.0.0.0'
PORT = 65432


# ---------------------------------------------------------------------------
# Framing helpers
# ---------------------------------------------------------------------------

def send_message(conn: socket.socket, payload: dict):
    """Sends a JSON payload with a 4-byte length prefix."""
    data = json.dumps(payload).encode('utf-8')
    header = struct.pack('>I', len(data))
    conn.sendall(header + data)


def recv_message(conn: socket.socket) -> dict:
    """
    Reads a length-prefixed message from the socket.
    Raises ConnectionError on incomplete/closed connection.
    """
    raw_header = _recv_exact(conn, 4)
    if not raw_header:
        raise ConnectionError("Connection closed by client")
    msg_len = struct.unpack('>I', raw_header)[0]
    if msg_len > 10 * 1024 * 1024:
        raise ConnectionError(f"Message too large: {msg_len} bytes")
    raw_body = _recv_exact(conn, msg_len)
    if not raw_body:
        raise ConnectionError("Connection closed while reading body")
    return json.loads(raw_body.decode('utf-8'))


def _recv_exact(conn: socket.socket, n: int) -> bytes:
    """Reads exactly n bytes from the socket, handling partial reads."""
    buf = b''
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            return b''
        buf += chunk
    return buf


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# ---------------------------------------------------------------------------
# Client handler
# ---------------------------------------------------------------------------

def handle_client(conn: socket.socket, addr):
    """Handles a single client connection in a dedicated thread."""
    print(f"[Server] New connection from {addr}")
    try:
        request = recv_message(conn)
        action = request.get("action", "")
        response = {"status": "error", "message": "Unknown action"}

        db_conn = get_connection()
        cursor = db_conn.cursor()

        # Auto-update competition statuses on every request
        update_competition_statuses(cursor)
        db_conn.commit()

        # ----------------------------------------------------------------
        # AUTH ROUTES
        # ----------------------------------------------------------------

        if action == "register":
            username = request.get('username', '').strip()
            email = request.get('email', '').strip()
            password = request.get('password', '')
            if not username or not email or not password:
                response = {"status": "error", "message": "Missing required fields"}
            else:
                hashed_pw = hash_password(password)
                try:
                    cursor.execute(
                        "INSERT INTO Users (username, email, password_hash) VALUES (?, ?, ?)",
                        (username, email, hashed_pw)
                    )
                    user_id = cursor.lastrowid
                    db_conn.commit()
                    create_initial_user_stats(user_id)
                    response = {"status": "success", "user_id": user_id,
                                "message": "User registered successfully"}
                    print(f"[Server] Registered new user: {username} (ID: {user_id})")
                except sqlite3.IntegrityError as e:
                    msg = str(e).lower()
                    if "username" in msg:
                        response = {"status": "error", "message": "Username already exists"}
                    elif "email" in msg:
                        response = {"status": "error", "message": "Email already registered"}
                    else:
                        response = {"status": "error", "message": "Database constraint error"}

        elif action == "login":
            username = request.get('username', '').strip()
            password = request.get('password', '')
            cursor.execute(
                "SELECT user_id, password_hash FROM Users WHERE username = ?", (username,)
            )
            user = cursor.fetchone()
            if user and hash_password(password) == user[1]:
                user_id = user[0]
                cursor.execute(
                    "UPDATE Users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?", (user_id,)
                )
                db_conn.commit()
                response = {"status": "success", "user_id": user_id,
                            "message": "Login successful"}
                print(f"[Server] User logged in: {username} (ID: {user_id})")
            else:
                response = {"status": "error", "message": "Invalid username or password"}

        # ----------------------------------------------------------------
        # SESSION ROUTES
        # ----------------------------------------------------------------

        elif action == "upload_session":
            user_id = request.get('user_id')
            session_data = request.get('session_data', {})
            if not user_id or not session_data:
                response = {"status": "error", "message": "Missing user_id or session_data"}
            else:
                cursor.execute("""
                    INSERT INTO Sessions
                        (user_id, start_time, end_time, focus_time_seconds,
                         distraction_count, description, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    session_data.get('start_time'),
                    session_data.get('end_time'),
                    session_data.get('focus_time_seconds', 0),
                    session_data.get('distraction_count', 0),
                    session_data.get('description', 'Focus Session'),
                    session_data.get('status', 'completed'),
                ))
                focus_time = session_data.get('focus_time_seconds', 0)
                distraction_count = session_data.get('distraction_count', 0)
                total_time = session_data.get('total_time_seconds', focus_time)
                session_score = StatsEngine.calculate_focus_score(
                    focus_time, total_time, distraction_count
                )
                cursor.execute("""
                    UPDATE CompetitionParticipants
                    SET total_focus_time_seconds = total_focus_time_seconds + ?,
                        sessions_count = sessions_count + 1,
                        focus_score = (
                            CASE WHEN sessions_count = 0 THEN ?
                            ELSE (focus_score * sessions_count + ?) / (sessions_count + 1)
                            END
                        )
                    WHERE user_id = ?
                      AND competition_id IN (
                          SELECT competition_id FROM Competitions
                          WHERE status = 'active'
                      )
                """, (focus_time, session_score, session_score, user_id))
                cursor.execute("""
                    SELECT DISTINCT competition_id FROM CompetitionParticipants
                    WHERE user_id = ?
                      AND competition_id IN (
                          SELECT competition_id FROM Competitions WHERE status = 'active'
                      )
                """, (user_id,))
                affected_competitions = [row[0] for row in cursor.fetchall()]
                for comp_id in affected_competitions:
                    recalculate_competition_ranks(comp_id, cursor)
                db_conn.commit()
                current_stats = get_user_stats(user_id)
                new_achievements = []
                if current_stats:
                    updated_stats = StatsEngine.calculate_updated_totals(
                        current_stats, session_data
                    )
                    update_user_stats(user_id, updated_stats)
                    new_achievements = check_and_grant_achievements(
                        user_id, updated_stats, cursor
                    )
                    db_conn.commit()
                response = {
                    "status": "success",
                    "message": "Session and stats updated successfully",
                    "new_achievements": new_achievements,
                    "session_score": session_score,
                }
                print(f"[Server] Session uploaded for user {user_id}. "
                      f"Focus: {focus_time}s, Score: {session_score}")

        elif action == "get_sessions":
            user_id = request.get("user_id")
            sessions = get_user_sessions(user_id)
            for s in sessions:
                s['start_time'] = str(s['start_time'])
                s['end_time'] = str(s['end_time'])
            response = {"status": "success", "sessions": sessions}

        # ----------------------------------------------------------------
        # USER PROFILE ROUTES
        # ----------------------------------------------------------------

        elif action == "get_user_profile":
            user_id = request.get("user_id")
            profile = get_user_profile(user_id)
            if profile:
                profile['created_at'] = str(profile.get('created_at', ''))
                response = {"status": "success", "profile": profile}
            else:
                response = {"status": "error", "message": "User not found"}

        elif action == "get_achievements":
            user_id = request.get("user_id")
            achievements = get_user_achievements(user_id)
            for a in achievements:
                a['unlocked_at'] = str(a['unlocked_at'])
            response = {"status": "success", "achievements": achievements}

        # ----------------------------------------------------------------
        # COMPETITION ROUTES
        # ----------------------------------------------------------------

        elif action == "create_competition":
            user_id = request.get("user_id")
            name = request.get("name", "").strip()
            start_date = request.get("start_date")
            end_date = request.get("end_date")
            description = request.get("description", "")
            max_participants = request.get("max_participants", 0)
            is_public = 1 if request.get("is_public", True) else 0
            if not name or not start_date or not end_date:
                response = {"status": "error", "message": "Missing required competition fields"}
            else:
                cursor.execute("""
                    INSERT INTO Competitions
                        (name, creator_id, start_date, end_date, description,
                         max_participants, is_public)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, user_id, start_date, end_date, description,
                      max_participants, is_public))
                comp_id = cursor.lastrowid
                cursor.execute("""
                    INSERT INTO CompetitionParticipants (competition_id, user_id)
                    VALUES (?, ?)
                """, (comp_id, user_id))
                db_conn.commit()
                response = {
                    "status": "success",
                    "room_code": comp_id,
                    "message": f"Competition '{name}' created! Share code: {comp_id}",
                }
                print(f"[Server] Competition created: '{name}' (ID: {comp_id}) by user {user_id}")

        elif action == "join_competition":
            user_id = request.get("user_id")
            room_code = request.get("competition_id")
            if not room_code:
                response = {"status": "error", "message": "Missing competition_id"}
            else:
                cursor.execute(
                    "SELECT competition_id, name, max_participants, status FROM Competitions WHERE competition_id = ?",
                    (int(room_code),)
                )
                comp = cursor.fetchone()
                if not comp:
                    response = {"status": "error", "message": "Competition not found"}
                elif comp[3] == 'ended':
                    response = {"status": "error", "message": "This competition has already ended"}
                else:
                    max_p = comp[2]
                    if max_p and max_p > 0:
                        cursor.execute(
                            "SELECT COUNT(*) FROM CompetitionParticipants WHERE competition_id = ?",
                            (int(room_code),)
                        )
                        count = cursor.fetchone()[0]
                        if count >= max_p:
                            db_conn.close()
                            send_message(conn, {"status": "error", "message": "Competition is full"})
                            return
                    try:
                        cursor.execute("""
                            INSERT INTO CompetitionParticipants (competition_id, user_id)
                            VALUES (?, ?)
                        """, (int(room_code), user_id))
                        db_conn.commit()
                        response = {
                            "status": "success",
                            "message": f"Successfully joined '{comp[1]}' (Code: {room_code})",
                        }
                        print(f"[Server] User {user_id} joined competition {room_code}")
                    except sqlite3.IntegrityError:
                        response = {"status": "error",
                                    "message": "You are already in this competition"}

        elif action == "leave_competition":
            user_id = request.get("user_id")
            room_code = request.get("competition_id")
            if not room_code:
                response = {"status": "error", "message": "Missing competition_id"}
            else:
                cursor.execute("""
                    DELETE FROM CompetitionParticipants
                    WHERE competition_id = ? AND user_id = ?
                """, (int(room_code), user_id))
                db_conn.commit()
                if cursor.rowcount > 0:
                    recalculate_competition_ranks(int(room_code), cursor)
                    db_conn.commit()
                    response = {"status": "success", "message": "Left the competition"}
                else:
                    response = {"status": "error",
                                "message": "You are not a participant in this competition"}

        elif action == "get_leaderboard":
            room_code = request.get("competition_id")
            if not room_code:
                response = {"status": "error", "message": "Missing competition_id"}
            else:
                cursor.execute("""
                    SELECT u.username,
                           cp.total_focus_time_seconds,
                           cp.sessions_count,
                           cp.focus_score,
                           cp.rank,
                           cp.joined_at
                    FROM CompetitionParticipants cp
                    JOIN Users u ON cp.user_id = u.user_id
                    WHERE cp.competition_id = ?
                    ORDER BY cp.total_focus_time_seconds DESC
                """, (int(room_code),))
                rows = cursor.fetchall()
                leaderboard = []
                for idx, row in enumerate(rows):
                    rank = row[4] if row[4] else idx + 1
                    leaderboard.append({
                        "rank": rank,
                        "username": row[0],
                        "focus_time": row[1],
                        "focus_time_formatted": StatsEngine.format_duration(row[1]),
                        "sessions_count": row[2],
                        "focus_score": round(row[3] or 0.0, 1),
                        "joined_at": str(row[5]),
                    })
                response = {"status": "success", "leaderboard": leaderboard}

        elif action == "get_global_leaderboard":
            limit = request.get("limit", 20)
            leaderboard = get_global_leaderboard(limit=int(limit))
            for entry in leaderboard:
                entry['focus_time_formatted'] = StatsEngine.format_duration(
                    entry.get('total_focus_time_seconds', 0)
                )
                entry['best_session_formatted'] = StatsEngine.format_duration(
                    entry.get('best_session_seconds', 0)
                )
            response = {"status": "success", "leaderboard": leaderboard}

        elif action == "get_user_competitions":
            user_id = request.get("user_id")
            cursor.execute("""
                SELECT c.competition_id, c.name, c.description, c.start_date, c.end_date,
                       c.status, c.is_public,
                       COUNT(cp2.user_id) AS participant_count,
                       cp.rank, cp.total_focus_time_seconds
                FROM Competitions c
                JOIN CompetitionParticipants cp ON c.competition_id = cp.competition_id
                LEFT JOIN CompetitionParticipants cp2 ON c.competition_id = cp2.competition_id
                WHERE cp.user_id = ?
                GROUP BY c.competition_id
                ORDER BY c.competition_id DESC
            """, (user_id,))
            rooms = []
            for row in cursor.fetchall():
                rooms.append({
                    "id": row[0],
                    "name": row[1],
                    "desc": row[2],
                    "start": str(row[3]),
                    "end": str(row[4]),
                    "status": row[5],
                    "is_public": bool(row[6]),
                    "participant_count": row[7],
                    "my_rank": row[8],
                    "my_focus_time": row[9],
                    "my_focus_time_formatted": StatsEngine.format_duration(row[9] or 0),
                })
            response = {"status": "success", "rooms": rooms}

        elif action == "get_competition_details":
            comp_id = request.get("competition_id")
            if not comp_id:
                response = {"status": "error", "message": "Missing competition_id"}
            else:
                details = get_competition_details(int(comp_id))
                if details:
                    details['start_date'] = str(details['start_date'])
                    details['end_date'] = str(details['end_date'])
                    details['created_at'] = str(details['created_at'])
                    response = {"status": "success", "competition": details}
                else:
                    response = {"status": "error", "message": "Competition not found"}

        elif action == "get_public_competitions":
            competitions = get_public_competitions()
            for c in competitions:
                c['start_date'] = str(c['start_date'])
                c['end_date'] = str(c['end_date'])
            response = {"status": "success", "competitions": competitions}

        else:
            response = {"status": "error", "message": f"Unknown action: '{action}'"}

        db_conn.close()
        send_message(conn, response)

    except ConnectionError as e:
        print(f"[Server] Connection error from {addr}: {e}")
    except json.JSONDecodeError as e:
        print(f"[Server] JSON decode error from {addr}: {e}")
        try:
            send_message(conn, {"status": "error", "message": "Invalid JSON"})
        except Exception:
            pass
    except Exception as e:
        print(f"[Server] Unhandled error from {addr}: {e}")
        import traceback
        traceback.print_exc()
        try:
            send_message(conn, {"status": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Server entry point
# ---------------------------------------------------------------------------

def start_server():
    init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.settimeout(1.0)
    server.listen(50)
    print(f"[Server] LockIn TCP server v2 listening on {HOST}:{PORT}")
    print(f"[Server] Protocol: 4-byte length-prefixed JSON framing")

    try:
        while True:
            try:
                conn, addr = server.accept()
                thread = threading.Thread(
                    target=handle_client, args=(conn, addr), daemon=True
                )
                thread.start()
            except socket.timeout:
                pass
    except KeyboardInterrupt:
        print("\n[Server] Shutting down gracefully. Goodbye!")
    finally:
        server.close()


if __name__ == "__main__":
    start_server()