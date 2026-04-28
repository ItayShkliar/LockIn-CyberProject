"""
Network Client Module (v2 - TCP with Length-Prefixed Framing)
=================================================================
Handles all TCP communication between the desktop app and the socket server.

Protocol: Every message is prefixed with a 4-byte big-endian integer that
indicates the byte length of the JSON payload that follows. This prevents
partial reads and stream fragmentation.

  Client sends: [4-byte length][JSON bytes]
  Server replies: [4-byte length][JSON bytes]
"""

import socket
import json
import struct
import os


class NetworkClient:
    def __init__(self, host="127.0.0.1", port=65432):
        self.host = host
        self.port = port
        self.logged_in_user_id = None
        self.logged_in_username = None
        self.cache_file = "offline_sessions.json"

    # -----------------------------------------------------------------------
    # Low-level framing helpers
    # -----------------------------------------------------------------------

    def _send_message(self, sock: socket.socket, payload: dict):
        """Sends a JSON payload with a 4-byte length prefix."""
        data = json.dumps(payload).encode("utf-8")
        header = struct.pack(">I", len(data))
        sock.sendall(header + data)

    def _recv_message(self, sock: socket.socket) -> dict:
        """Reads a length-prefixed message and returns the decoded dict."""
        raw_header = self._recv_exact(sock, 4)
        if not raw_header:
            raise ConnectionError("Server closed the connection")
        msg_len = struct.unpack(">I", raw_header)[0]
        if msg_len > 10 * 1024 * 1024:
            raise ConnectionError(f"Response too large: {msg_len} bytes")
        raw_body = self._recv_exact(sock, msg_len)
        if not raw_body:
            raise ConnectionError("Server closed connection while reading body")
        return json.loads(raw_body.decode("utf-8"))

    def _recv_exact(self, sock: socket.socket, n: int) -> bytes:
        """Reads exactly n bytes from the socket."""
        buf = b""
        while len(buf) < n:
            chunk = sock.recv(n - len(buf))
            if not chunk:
                return b""
            buf += chunk
        return buf

    def _send_request(self, payload: dict) -> dict:
        """Opens a connection, sends a request, receives a response, closes."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            try:
                s.connect((self.host, self.port))
                self._send_message(s, payload)
                return self._recv_message(s)
            except (socket.timeout, ConnectionRefusedError, OSError) as e:
                raise ConnectionError(f"Connection failed: {e}")

    # -----------------------------------------------------------------------
    # Auth routes
    # -----------------------------------------------------------------------

    def register(self, username: str, email: str, password: str) -> dict:
        payload = {"action": "register", "username": username,
                   "email": email, "password": password}
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    def login(self, username: str, password: str) -> dict:
        payload = {"action": "login", "username": username, "password": password}
        try:
            response = self._send_request(payload)
            if response.get("status") == "success":
                self.logged_in_user_id = response.get("user_id")
                self.logged_in_username = username
                self.sync_offline_sessions()
            return response
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    def logout(self):
        """Clears the local session state."""
        self.logged_in_user_id = None
        self.logged_in_username = None

    # -----------------------------------------------------------------------
    # Session routes
    # -----------------------------------------------------------------------

    def upload_session(self, session_data: dict) -> dict:
        if not self.logged_in_user_id:
            return {"status": "error", "message": "User not logged in."}
        payload = {
            "action": "upload_session",
            "user_id": self.logged_in_user_id,
            "session_data": session_data,
        }
        try:
            return self._send_request(payload)
        except ConnectionError:
            self._save_offline(payload)
            return {"status": "offline", "message": "Server unreachable. Session saved locally!"}

    def get_sessions(self, user_id: int) -> dict:
        payload = {"action": "get_sessions", "user_id": user_id}
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    # -----------------------------------------------------------------------
    # User profile routes
    # -----------------------------------------------------------------------

    def get_user_profile(self) -> dict:
        if not self.logged_in_user_id:
            return {"status": "error", "message": "Not logged in"}
        payload = {"action": "get_user_profile", "user_id": self.logged_in_user_id}
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    def get_achievements(self) -> dict:
        if not self.logged_in_user_id:
            return {"status": "error", "message": "Not logged in"}
        payload = {"action": "get_achievements", "user_id": self.logged_in_user_id}
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    # -----------------------------------------------------------------------
    # Competition routes
    # -----------------------------------------------------------------------

    def create_competition(self, name: str, start_date: str, end_date: str,
                           description: str = "", max_participants: int = 0,
                           is_public: bool = True, focus_apps: list = None) -> dict:
        if not self.logged_in_user_id:
            return {"status": "error", "message": "Must be logged in to create a competition."}
        payload = {
            "action": "create_competition",
            "user_id": self.logged_in_user_id,
            "name": name,
            "start_date": start_date,
            "end_date": end_date,
            "description": description,
            "max_participants": max_participants,
            "is_public": is_public,
            "focus_apps": focus_apps or [],
        }
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    def join_competition(self, room_code: int) -> dict:
        if not self.logged_in_user_id:
            return {"status": "error", "message": "Must be logged in to join a competition."}
        payload = {
            "action": "join_competition",
            "user_id": self.logged_in_user_id,
            "competition_id": int(room_code),
        }
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    def leave_competition(self, room_code: int) -> dict:
        if not self.logged_in_user_id:
            return {"status": "error", "message": "Not logged in"}
        payload = {
            "action": "leave_competition",
            "user_id": self.logged_in_user_id,
            "competition_id": int(room_code),
        }
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    def get_leaderboard(self, room_code: int) -> dict:
        payload = {"action": "get_leaderboard", "competition_id": int(room_code)}
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    def get_global_leaderboard(self, limit: int = 20) -> dict:
        payload = {"action": "get_global_leaderboard", "limit": limit}
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    def get_user_competitions(self) -> dict:
        if not self.logged_in_user_id:
            return {"status": "error", "message": "Not logged in"}
        payload = {"action": "get_user_competitions", "user_id": self.logged_in_user_id}
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    def get_competition_details(self, competition_id: int) -> dict:
        payload = {"action": "get_competition_details", "competition_id": int(competition_id)}
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    def get_public_competitions(self) -> dict:
        payload = {"action": "get_public_competitions"}
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    # -----------------------------------------------------------------------
    # Offline sync helpers
    # -----------------------------------------------------------------------

    def _save_offline(self, payload: dict):
        offline_data = []
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    offline_data = json.load(f)
            except Exception:
                pass
        offline_data.append(payload)
        with open(self.cache_file, "w") as f:
            json.dump(offline_data, f, indent=4)
        print("[Network] Session cached locally due to connection error.")

    def get_daily_stats(self):
        """Fetches today's focus stats for the logged-in user."""
        if not self.logged_in_user_id:
            return {"status": "error", "message": "Not logged in"}
        return self._send_request({
            "action": "get_daily_stats",
            "user_id": self.logged_in_user_id,
        })

    def get_active_competition_leaderboard(self):
        """Fetches all active competitions the user is in, with their rank."""
        if not self.logged_in_user_id:
            return {"status": "error", "message": "Not logged in"}
        return self._send_request({
            "action": "get_active_competition_leaderboard",
            "user_id": self.logged_in_user_id,
        })

    def sync_offline_sessions(self):
        """Attempts to upload any locally cached sessions to the server."""
        if not os.path.exists(self.cache_file) or not self.logged_in_user_id:
            return
        try:
            with open(self.cache_file, "r") as f:
                offline_data = json.load(f)
        except Exception:
            return
        print(f"[Network] Attempting to sync {len(offline_data)} offline sessions...")
        remaining_data = []
        for payload in offline_data:
            payload["user_id"] = self.logged_in_user_id
            payload["action"] = "upload_session"
            try:
                response = self._send_request(payload)
                if response.get("status") == "success":
                    print("[Network] Successfully synced offline session!")
                else:
                    remaining_data.append(payload)
            except ConnectionError:
                remaining_data.append(payload)
        if not remaining_data:
            os.remove(self.cache_file)
            print("[Network] All offline sessions synced and cache cleared.")
        else:
            with open(self.cache_file, "w") as f:
                json.dump(remaining_data, f, indent=4)

    @staticmethod
    def get_achievement_name(ach_id: str) -> str:
        """Translates backend achievement IDs to friendly names."""
        mapping = {
            "first_session": "First Step", "sessions_10": "Dedicated",
            "sessions_50": "Focused", "sessions_100": "Elite Focuser",
            "focus_1h": "One Hour Club", "focus_10h": "Ten Hour Warrior",
            "focus_100h": "Century Focuser", "streak_3": "On a Roll",
            "streak_7": "Week Warrior", "streak_30": "Monthly Master",
        }
        return mapping.get(ach_id, ach_id)
