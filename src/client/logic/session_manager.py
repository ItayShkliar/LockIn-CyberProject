"""
Session Manager Module
Coordinates the focus session, tracks time, calculates the Focus Score,
and manages the underlying AppMonitor.
"""
import time
from logic.app_monitor import AppMonitor

class SessionManager:
    """
    Manages the lifecycle of a focus session.
    """
    
    def __init__(self):
        self._monitor = AppMonitor([])
        self.is_active = False
        self.start_time = 0
        
        # Penalty points for each distraction (based on design document concept)
        self.penalty_per_distraction = 5 

    def start_session(self, blocked_apps: list):
        """Starts the focus session and the background monitor."""
        self._monitor.update_blocked_apps(blocked_apps)
        self._monitor.start_session()
        
        self.start_time = time.time()
        self.is_active = True
        print("[SessionManager] Session started.")

    def stop_session(self) -> dict:
        """Stops the session and returns the final statistics."""
        distractions = self._monitor.stop_session()
        self.is_active = False
        total_time = int(time.time() - self.start_time)
        
        final_score = self._calculate_score(distractions)
        print(f"[SessionManager] Session ended. Score: {final_score}, Distractions: {distractions}")
        
        return {
            "time_seconds": total_time,
            "distractions": distractions,
            "final_score": final_score
        }

    def get_current_stats(self) -> tuple:
        """
        Returns real-time stats for the UI.
        Returns: (elapsed_seconds, distractions, current_score)
        """
        if not self.is_active:
            return 0, 0, 100
            
        elapsed = int(time.time() - self.start_time)
        distractions = self._monitor._distraction_count 
        score = self._calculate_score(distractions)
        
        return elapsed, distractions, score

    def _calculate_score(self, distractions: int) -> int:
        """Calculates the Focus Score. Score cannot drop below 0."""
        score = 100 - (distractions * self.penalty_per_distraction)
        return max(0, score)