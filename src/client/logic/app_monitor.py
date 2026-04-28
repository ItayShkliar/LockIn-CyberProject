"""
App Monitor Module
Tracks the active foreground window to measure focus time and distractions.

Enhanced with browser tab awareness:
  - When a browser is in the foreground, the monitor reads the window title
    to determine which website/tab the user is viewing.
  - If the user specified focus tab keywords, only matching browser tabs
    count as focused time.  Non-matching tabs count as distractions.
"""
import time
import threading
import ctypes
import psutil

# Known browser executable names (lowercase)
BROWSER_PROCESSES = {'chrome.exe', 'msedge.exe', 'brave.exe', 'firefox.exe', 'opera.exe'}


class AppMonitor:
    """
    Handles OS-level window tracking.  Runs in a background thread and counts
    how many seconds the user spends on focused apps vs distracted apps.
    Now also tracks browser tab titles for granular website-level monitoring.
    """

    def __init__(self):
        self._is_running = False
        self._focus_apps = []
        self._focus_tabs = []          # NEW: keywords for allowed browser tabs

        self.total_seconds = 0
        self.focus_seconds = 0
        self.distractions = 0

        self._monitor_thread = None
        self._was_focusing_last_tick = True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_monitoring(self, focus_apps: list, focus_tabs: list = None):
        """Starts the background tracking thread.
        
        Args:
            focus_apps:  List of process names the user wants to focus on.
            focus_tabs:  Optional list of keyword strings.  When a browser is
                         the foreground app, the window title must contain at
                         least one of these keywords for the tick to count as
                         focused.  If empty/None, *all* browser usage counts
                         as focused (as long as the browser is in focus_apps).
        """
        self._focus_apps = [app.lower() for app in focus_apps]
        self._focus_tabs = [kw.lower() for kw in (focus_tabs or [])]
        self._is_running = True

        self.total_seconds = 0
        self.focus_seconds = 0
        self.distractions = 0
        self._was_focusing_last_tick = True

        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print(f"[Monitor] Started tracking. Focus apps: {self._focus_apps}")
        if self._focus_tabs:
            print(f"[Monitor] Focus tab keywords: {self._focus_tabs}")

    def stop_monitoring(self) -> tuple:
        """Stops the tracking thread and returns the final raw metrics."""
        self._is_running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
        return self.total_seconds, self.focus_seconds, self.distractions

    def get_current_stats(self) -> tuple:
        """Returns the raw tracking stats at this exact moment."""
        return self.total_seconds, self.focus_seconds, self.distractions

    # ------------------------------------------------------------------
    # Windows API helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_foreground_info() -> tuple:
        """Returns (process_name, window_title) for the current foreground window.
        
        Both values are lowercase.  Returns (None, None) on failure.
        """
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                return None, None

            # --- Get the process name via PID ---
            pid = ctypes.c_ulong(0)
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            proc_name = None
            if pid.value > 0:
                proc_name = psutil.Process(pid.value).name().lower()

            # --- Get the window title ---
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            title = ""
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value.lower()

            return proc_name, title
        except Exception:
            return None, None

    # ------------------------------------------------------------------
    # Core loop
    # ------------------------------------------------------------------

    def _is_browser(self, proc_name: str) -> bool:
        """Returns True if the process is a known web browser."""
        return proc_name in BROWSER_PROCESSES

    def _monitor_loop(self):
        """Runs every second to check if the user is staying on task."""
        while self._is_running:
            time.sleep(1)
            self.total_seconds += 1

            proc_name, win_title = self._get_foreground_info()

            if proc_name:
                # Step 1: Is this process in the focus apps list?
                is_focus_app = any(
                    focus.replace('.exe', '') in proc_name
                    for focus in self._focus_apps
                )

                # Step 2: If it's a browser AND we have tab keywords, refine
                if is_focus_app and self._is_browser(proc_name) and self._focus_tabs:
                    # The app matches, but we need to verify the tab title
                    tab_matches = any(kw in win_title for kw in self._focus_tabs)
                    if tab_matches:
                        is_focusing = True
                    else:
                        is_focusing = False
                else:
                    is_focusing = is_focus_app

                # Step 3: Update counters
                if is_focusing:
                    self.focus_seconds += 1
                    self._was_focusing_last_tick = True
                else:
                    if self._was_focusing_last_tick:
                        self.distractions += 1
                        distraction_detail = f"{proc_name}"
                        if self._is_browser(proc_name) and win_title:
                            distraction_detail = f"{proc_name} → {win_title[:60]}"
                        print(f"[Monitor] Distraction logged! → {distraction_detail}")
                    self._was_focusing_last_tick = False