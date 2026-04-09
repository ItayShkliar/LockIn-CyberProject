"""
Network Client Module (Raw Sockets)
Handles all TCP communication between the local desktop app and the custom socket server.
"""
import socket
import json
import os

class NetworkClient:
    def __init__(self, host="127.0.0.1", port=65432):
        self.host = host
        self.port = port
        self.logged_in_user_id = None 
        self.cache_file = "offline_sessions.json"

    def _send_request(self, payload: dict) -> dict:
        """Helper method to send a dictionary to the socket server and get a dictionary back."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # 5-second timeout, equivalent to requests timeout=5
            try:
                s.connect((self.host, self.port))
                # Send the JSON payload encoded as bytes
                s.sendall(json.dumps(payload).encode('utf-8'))
                
                # Wait for the response
                data = s.recv(8192) # Receive up to 8KB of data
                if not data:
                    return {"status": "error", "message": "Empty response from server"}
                    
                return json.loads(data.decode('utf-8'))
            except (socket.timeout, ConnectionRefusedError, Exception) as e:
                raise ConnectionError(f"Connection failed: {e}")

    def register(self, username, email, password) -> dict:
        payload = {
            "action": "register",
            "username": username, 
            "email": email, 
            "password": password
        }
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    def login(self, username, password) -> dict:
        payload = {
            "action": "login",
            "username": username, 
            "password": password
        }
        try:
            response = self._send_request(payload)
            if response.get("status") == "success":
                self.logged_in_user_id = response.get("user_id")
            return response
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    def upload_session(self, session_data: dict) -> dict:
        if not self.logged_in_user_id:
            return {"status": "error", "message": "User not logged in. Cannot upload session."}
            
        payload = {
            "action": "upload_session",
            "user_id": self.logged_in_user_id,
            "session_data": session_data
        }
        
        try:
            return self._send_request(payload)
        except ConnectionError:
            # ---> THE SERVER IS DOWN OR NO INTERNET: SAVE LOCALLY <---
            self._save_offline(payload)
            return {"status": "offline", "message": "Server unreachable. Session saved locally!"}

    def _save_offline(self, payload: dict):
        offline_data = []
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    offline_data = json.load(f)
            except:
                pass 
                
        offline_data.append(payload)
        
        with open(self.cache_file, 'w') as f:
            json.dump(offline_data, f, indent=4)
        print("[Network] Session cached locally due to connection error.")

    def sync_offline_sessions(self):
        if not os.path.exists(self.cache_file) or not self.logged_in_user_id:
            return 

        try:
            with open(self.cache_file, 'r') as f:
                offline_data = json.load(f)
        except:
            return

        print(f"[Network] Attempting to sync {len(offline_data)} offline sessions...")
        remaining_data = []

        for payload in offline_data:
            payload['user_id'] = self.logged_in_user_id 
            try:
                # Ensure the action is set correctly for offline payloads
                payload['action'] = "upload_session"
                response = self._send_request(payload)
                if response.get("status") == "success":
                    print(f"[Network] Successfully synced offline session!")
                else:
                    remaining_data.append(payload) 
            except ConnectionError:
                remaining_data.append(payload) 
                
        if not remaining_data:
            os.remove(self.cache_file)
            print("[Network] All offline sessions synced and cache cleared.")
        else:
            with open(self.cache_file, 'w') as f:
                json.dump(remaining_data, f, indent=4)
    
    def get_sessions(self, user_id: int) -> dict:
        """Fetches the user's session history from the server."""
        payload = {
            "action": "get_sessions",
            "user_id": user_id
        }
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}
        
    def create_competition(self, name: str, start_date: str, end_date: str, description: str = "") -> dict:
        """Creates a new competition room and automatically joins the creator."""
        if not self.logged_in_user_id:
            return {"status": "error", "message": "Must be logged in to create a room."}

        payload = {
            "action": "create_competition",
            "user_id": self.logged_in_user_id,
            "name": name,
            "start_date": start_date,
            "end_date": end_date,
            "description": description
        }
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    def join_competition(self, room_code: int) -> dict:
        """Joins an existing competition using the room code (competition_id)."""
        if not self.logged_in_user_id:
            return {"status": "error", "message": "Must be logged in to join a room."}

        payload = {
            "action": "join_competition",
            "user_id": self.logged_in_user_id,
            "competition_id": int(room_code)
        }
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

    def get_leaderboard(self, room_code: int) -> dict:
        """Fetches the participants of a room ordered by total focus time."""
        payload = {
            "action": "get_leaderboard",
            "competition_id": int(room_code)
        }
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}
    
    def get_user_competitions(self) -> dict:
        """Fetches a list of all rooms the current user is participating in."""
        if not self.logged_in_user_id:
            return {"status": "error", "message": "Not logged in"}
            
        payload = {
            "action": "get_user_competitions",
            "user_id": self.logged_in_user_id
        }
        try:
            return self._send_request(payload)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}