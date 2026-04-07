"""
Session Manager Module
Manages session lifecycle and calculates business metrics like Focus Score.
Delegates OS tracking to AppMonitor.
"""
from logic.app_monitor import AppMonitor
from logic.app_scanner import AppScanner # <-- Added this!

class SessionManager:
    def __init__(self):
        self.is_active = False
        self._monitor = AppMonitor() 
        self._scanner = AppScanner() # <-- Added this!

    def start_session(self, focus_apps: list):
        self.is_active = True
        self._monitor.start_monitoring(focus_apps)
        print("[Session] Session started.")

    def stop_session(self) -> dict:
        self.is_active = False
        total, focus, dists = self._monitor.stop_monitoring()
        _, _, _, final_score = self.get_current_stats()
            
        return {
            "total_time_seconds": total,
            "focus_time_seconds": focus,
            "distractions": dists,
            "final_score": final_score
        }

    def get_current_stats(self) -> tuple:
        total_sec, focus_sec, distractions = self._monitor.get_current_stats()
        
        score = 0
        if total_sec > 0:
            base_score = (focus_sec / total_sec) * 100
            penalty = distractions * 5
            score = int(max(0, base_score - penalty)) 
            
        return total_sec, focus_sec, distractions, score
    
    def get_available_apps(self) -> list:
        # Use the actual scanner now!
        return self._scanner.get_running_processes()