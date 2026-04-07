"""
Network Client Module
Handles all HTTP communication between the local desktop app and the remote Flask server.
"""
import requests
import json
import os

class NetworkClient:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.logged_in_user_id = None 
        self.cache_file = "offline_sessions.json"

    def register(self, username, email, password) -> dict:
        url = f"{self.base_url}/api/user/register"
        payload = {"username": username, "email": email, "password": password}
        try:
            response = self.session.post(url, json=payload, timeout=5)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Connection error: {e}"}

    def login(self, username, password) -> dict:
        url = f"{self.base_url}/api/user/login"
        payload = {"username": username, "password": password}
        try:
            response = self.session.post(url, json=payload, timeout=5)
            data = response.json()
            if data.get("status") == "success":
                self.logged_in_user_id = data.get("user_id")
            return data
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Connection error: {e}"}

    def upload_session(self, session_data: dict) -> dict:
        if not self.logged_in_user_id:
            return {"status": "error", "message": "User not logged in. Cannot upload session."}
            
        url = f"{self.base_url}/api/session/upload"
        payload = {
            "user_id": self.logged_in_user_id,
            "session_data": session_data
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=5)
            return response.json()
        except requests.exceptions.RequestException:
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
        url = f"{self.base_url}/api/session/upload"

        for payload in offline_data:
            payload['user_id'] = self.logged_in_user_id 
            try:
                response = self.session.post(url, json=payload, timeout=5)
                if response.status_code == 201:
                    print(f"[Network] Successfully synced offline session!")
                else:
                    remaining_data.append(payload) 
            except requests.exceptions.RequestException:
                remaining_data.append(payload) 
                
        if not remaining_data:
            os.remove(self.cache_file)
            print("[Network] All offline sessions synced and cache cleared.")
        else:
            with open(self.cache_file, 'w') as f:
                json.dump(remaining_data, f, indent=4)