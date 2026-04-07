"""
Session Manager Module
Manages session lifecycle and calculates business metrics like Focus Score.
Delegates OS tracking to AppMonitor.
"""
from logic.app_monitor import AppMonitor

class SessionManager:
    """
    Manages the overarching Focus Session and calculates the Focus Score.
    """
    def __init__(self):
        self.is_active = False
        self._monitor = AppMonitor() # Instantiate our tracking module

    def start_session(self, focus_apps: list):
        """Starts the session and delegates tracking to the AppMonitor."""
        self.is_active = True
        self._monitor.start_monitoring(focus_apps)
        print("[Session] Session started.")

    def stop_session(self) -> dict:
        """Stops the session, retrieves final stats, and calculates the score."""
        self.is_active = False
        
        # Stop the monitor and get the final raw numbers
        total, focus, dists = self._monitor.stop_monitoring()
        
        # Use our own method to calculate the final Focus Score
        _, _, _, final_score = self.get_current_stats()
            
        return {
            "total_time_seconds": total,
            "focus_time_seconds": focus,
            "distractions": dists,
            "final_score": final_score
        }

    def get_current_stats(self) -> tuple:
        """Retrieves live stats from the monitor and calculates the Focus Score."""
        
        # Ask the monitor for the raw OS data
        total_sec, focus_sec, distractions = self._monitor.get_current_stats()
        
        score = 0
        if total_sec > 0:
            # Focus Score = (Focus Time / Total Time) * 100 - (Distractions * 5)
            base_score = (focus_sec / total_sec) * 100
            penalty = distractions * 5
            score = int(max(0, base_score - penalty)) # Prevent negative scores
            
        return total_sec, focus_sec, distractions, score