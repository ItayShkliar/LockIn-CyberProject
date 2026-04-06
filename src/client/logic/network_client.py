"""
Network Client Module
Handles all HTTP communication between the local desktop app and the remote Flask server.
"""
import requests

class NetworkClient:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.logged_in_user_id = None 

    def register(self, username, email, password) -> dict:
        """Sends a registration request to the server."""
        url = f"{self.base_url}/api/user/register"
        payload = {"username": username, "email": email, "password": password}
        
        try:
            response = self.session.post(url, json=payload, timeout=5)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Connection error: {e}"}

    def login(self, username, password) -> dict:
        """Sends a login request to the server."""
        url = f"{self.base_url}/api/user/login"
        payload = {"username": username, "password": password}
        
        try:
            response = self.session.post(url, json=payload, timeout=5)
            data = response.json()
            
            # Save the user ID if login was successful
            if data.get("status") == "success":
                self.logged_in_user_id = data.get("user_id")
                
            return data
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Connection error: {e}"}
        
    def upload_session(self, session_data: dict) -> dict:
        """Sends a completed focus session to the server."""
        # Check if the user is actually logged in before trying to send data
        if not self.logged_in_user_id:
            return {"status": "error", "message": "User not logged in. Cannot upload session."}
            
        url = f"{self.base_url}/api/session/upload"
        
        # Package the data exactly how our Flask API expects it
        payload = {
            "user_id": self.logged_in_user_id,
            "session_data": session_data
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=5)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Connection error: {e}"}