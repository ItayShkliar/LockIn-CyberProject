"""
App Monitor Module
Tracks the active foreground window to measure focus time and distractions.
"""
import time
import threading
import ctypes
import psutil

class AppMonitor:
    """
    Handles OS-level window tracking. Runs in a background thread and counts 
    how many seconds the user spends on focused apps vs distracted apps.
    """
    def __init__(self):
        self._is_running = False
        self._focus_apps = []
        
        self.total_seconds = 0
        self.focus_seconds = 0
        self.distractions = 0
        
        self._monitor_thread = None
        self._was_focusing_last_tick = True

    def start_monitoring(self, focus_apps: list):
        """Starts the background tracking thread."""
        self._focus_apps = [app.lower() for app in focus_apps]
        self._is_running = True
        
        self.total_seconds = 0
        self.focus_seconds = 0
        self.distractions = 0
        self._was_focusing_last_tick = True
        
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print(f"[Monitor] Started tracking. Focus apps: {self._focus_apps}")

    def stop_monitoring(self) -> tuple:
        """Stops the tracking thread and returns the final raw metrics."""
        self._is_running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
        return self.total_seconds, self.focus_seconds, self.distractions

    def get_current_stats(self) -> tuple:
        """Returns the raw tracking stats at this exact moment."""
        return self.total_seconds, self.focus_seconds, self.distractions

    def _get_active_process_name(self):
        """Asks Windows what app is currently in the foreground."""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd: return None
            
            pid = ctypes.c_ulong(0)
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            if pid.value > 0:
                return psutil.Process(pid.value).name().lower()
        except Exception:
            pass
        return None

    def _monitor_loop(self):
        """Runs every second to check if the user is staying on task."""
        while self._is_running:
            time.sleep(1)
            self.total_seconds += 1
            
            active_app = self._get_active_process_name()
            
            if active_app:
                is_focusing = any(focus.replace('.exe', '') in active_app for focus in self._focus_apps)
                
                if is_focusing:
                    self.focus_seconds += 1
                    self._was_focusing_last_tick = True
                else:
                    if self._was_focusing_last_tick:
                        self.distractions += 1
                        print(f"[Monitor] Distraction logged! Switched to: {active_app}")
                    self._was_focusing_last_tick = False