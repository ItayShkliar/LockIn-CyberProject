"""
Config Manager Module
Handles saving and loading user preferences (like blocked apps) 
so they persist even after the app is closed.
"""
import json
import os

class ConfigManager:
    """
    Manages reading and writing application settings to a local JSON file.
    """
    def __init__(self, config_file="lockin_config.json"):
        # This saves the file in the main project directory
        self.config_file = config_file
        
        # Default settings if the file doesn't exist yet
        self.default_config = {
            "blocked_apps": []
        }

    def load_config(self) -> dict:
        """Loads the configuration from the JSON file."""
        if not os.path.exists(self.config_file):
            print("[Config] No config file found. Creating a default one.")
            self.save_config(self.default_config)
            return self.default_config

        try:
            with open(self.config_file, 'r') as file:
                data = json.load(file)
                print(f"[Config] Loaded settings: {data}")
                return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Config] Error loading config: {e}. Returning defaults.")
            return self.default_config

    def save_config(self, config_data: dict):
        """Saves the given dictionary to the JSON file."""
        try:
            with open(self.config_file, 'w') as file:
                json.dump(config_data, file, indent=4)
                print("[Config] Settings saved successfully.")
        except IOError as e:
            print(f"[Config] Failed to save config: {e}")