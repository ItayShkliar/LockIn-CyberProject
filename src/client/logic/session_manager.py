"""
Session Manager Module
Tracks total session time, active focus time, and calculates the Focus Score.
"""
import time
import threading
import ctypes
import psutil

class SessionManager:
    def __init__(self):
        self.is_active = False
        self.focus_apps = [] # The apps the user WANTS to use
        
        self.total_seconds = 0
        self.focus_seconds = 0
        self.distractions = 0
        
        self._monitor_thread = None
        self._was_focusing_last_tick = True

    def start_session(self, focus_apps: list):
        """Starts the timer and background monitoring."""
        # Convert to lowercase for easier matching (e.g., 'Code.exe' -> 'code.exe')
        self.focus_apps = [app.lower() for app in focus_apps] 
        self.is_active = True
        
        self.total_seconds = 0
        self.focus_seconds = 0
        self.distractions = 0
        self._was_focusing_last_tick = True
        
        # Start monitoring the active window in the background
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print(f"[Session] Started. Focusing on: {self.focus_apps}")

    def stop_session(self) -> dict:
        """Stops the session and returns the final stats."""
        self.is_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
            
        # FIX: We now unpack all 4 values returned by get_current_stats!
        # (total_seconds, focus_seconds, distractions, final_score)
        _, _, _, final_score = self.get_current_stats()
            
        return {
            "total_time_seconds": self.total_seconds,
            "focus_time_seconds": self.focus_seconds,
            "distractions": self.distractions,
            "final_score": final_score
        }

    def get_current_stats(self) -> tuple:
        """Returns (total_time, focus_time, distractions, score) for the UI."""
        score = 0
        if self.total_seconds > 0:
            # The algorithm from your Design Doc!
            # Focus Score = (Focus Time / Total Time) * 100 - (Distractions * 5)
            base_score = (self.focus_seconds / self.total_seconds) * 100
            penalty = self.distractions * 5
            score = int(max(0, base_score - penalty)) # Prevent negative scores
            
        return self.total_seconds, self.focus_seconds, self.distractions, score

    def _get_active_process_name(self):
        """Asks Windows what app is currently in the foreground."""
        try:
            # Get the ID of the window the user is currently interacting with
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd: return None
            
            pid = ctypes.c_ulong(0)
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            # Find the application name belonging to that ID
            if pid.value > 0:
                return psutil.Process(pid.value).name().lower()
        except Exception:
            pass
        return None

    def _monitor_loop(self):
        """Runs every second to check if the user is staying on task."""
        while self.is_active:
            time.sleep(1)
            self.total_seconds += 1
            
            active_app = self._get_active_process_name()
            
            if active_app:
                # Check if the active app is one of the user's chosen Focus Apps
                # (e.g. if 'code' is in 'code.exe')
                is_focusing = any(focus.replace('.exe', '') in active_app for focus in self.focus_apps)
                
                if is_focusing:
                    self.focus_seconds += 1
                    self._was_focusing_last_tick = True
                else:
                    # If they WERE focusing, but now they aren't, they got distracted!
                    if self._was_focusing_last_tick:
                        self.distractions += 1
                        print(f"[Session] Distraction logged! Switched to: {active_app}")
                    self._was_focusing_last_tick = False