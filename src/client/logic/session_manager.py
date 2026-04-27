"""
Session Manager Module
Manages session lifecycle and calculates business metrics like Focus Score.
Delegates OS tracking to AppMonitor.
"""
from logic.app_monitor import AppMonitor
from logic.app_scanner import AppScanner 
from datetime import datetime

class SessionManager:
    def __init__(self):
        self.is_active = False
        self._monitor = AppMonitor() 
        self._scanner = AppScanner() 
        
        self.start_time = None
        self.description = ""

    def start_session(self, focus_apps: list, description: str = "Focus Session"): # <-- Accept description
        self.is_active = True
        self.description = description
        # Capture exactly when they clicked Start (Format: YYYY-MM-DD HH:MM:SS)
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        self._monitor.start_monitoring(focus_apps)
        print(f"[Session] Started: {self.description}")

    def stop_session(self) -> dict:
        self.is_active = False
        total, focus, dists = self._monitor.stop_monitoring()
        _, _, _, final_score = self.get_current_stats()
        
        # Capture exactly when they clicked Stop
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        return {
            "start_time": self.start_time, 
            "end_time": end_time,             
            "description": self.description, 
            "total_time_seconds": total,
            "focus_time_seconds": focus,
            "distraction_count": dists,   
            "final_score": final_score,
            "status": "completed"   
        }

    def get_current_stats(self) -> tuple:
        total_sec, focus_sec, distractions = self._monitor.get_current_stats()
        
        import sys
        import os
        src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if src_dir not in sys.path:
            sys.path.append(src_dir)
        from server.logic.stats_engine import StatsEngine
        
        score = int(StatsEngine.calculate_focus_score(focus_sec, total_sec, distractions))
            
        return total_sec, focus_sec, distractions, score
    
    
    def get_available_apps(self) -> list:
        # Use the actual scanner now!
        return self._scanner.get_running_processes()

    @staticmethod
    def format_seconds(seconds: int) -> str:
        h, r = divmod(seconds, 3600)
        m, s = divmod(r, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def get_session_summary(self, stats: dict) -> str:
        """Returns a human-readable summary of the session results."""
        total = self.format_seconds(stats.get("total_time_seconds", 0))
        focus = self.format_seconds(stats.get("focus_time_seconds", 0))
        dists = stats.get("distraction_count", 0)
        score = stats.get("final_score", 0)
        desc = stats.get("description", "Focus Session")
        
        return (
            f"Task: {desc}\n"
            f"Total Time: {total}\n"
            f"Focus Time: {focus}\n"
            f"Distractions: {dists}\n"
            f"Focus Score: {score}"
        )