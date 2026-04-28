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
import ctypes.wintypes
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
        self._focus_tabs = []          # keywords for allowed browser tabs

        self.total_seconds = 0
        self.focus_seconds = 0
        self.distractions = 0
        self.app_focus_times = {}      # per-app breakdown: {'code.exe': 120, ...}

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
        self._focus_tabs = [kw.lower().strip() for kw in (focus_tabs or []) if kw.strip()]
        self._is_running = True

        self.total_seconds = 0
        self.focus_seconds = 0
        self.distractions = 0
        self.app_focus_times = {}
        self._was_focusing_last_tick = True

        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print(f"[Monitor] Started tracking. Focus apps: {self._focus_apps}")
        if self._focus_tabs:
            print(f"[Monitor] Focus tab keywords: {self._focus_tabs}")

    def stop_monitoring(self) -> tuple:
        """Stops the tracking thread and returns (total, focus, distractions, app_focus_times)."""
        self._is_running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
        return self.total_seconds, self.focus_seconds, self.distractions, dict(self.app_focus_times)

    def get_current_stats(self) -> tuple:
        """Returns (total, focus, distractions, app_focus_times) at this moment."""
        return self.total_seconds, self.focus_seconds, self.distractions, dict(self.app_focus_times)

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

            # --- Get the window title FIRST (most reliable) ---
            title = ""
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value

            # --- Get the process name via PID ---
            pid = ctypes.c_ulong(0)
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            proc_name = None
            if pid.value > 0:
                proc_name = psutil.Process(pid.value).name().lower()

            return proc_name, title
        except Exception:
            return None, None

    # ------------------------------------------------------------------
    # Matching logic (public for testability)
    # ------------------------------------------------------------------

    def check_focus(self, proc_name: str, win_title: str) -> bool:
        """Determines if the current foreground window counts as 'focused'.
        
        This method is extracted so it can be unit-tested directly.
        
        Args:
            proc_name: Lowercase process name (e.g. 'chrome.exe').
            win_title: Original window title (will be lowercased internally).
            
        Returns:
            True if the user is considered to be on-task.
        """
        if not proc_name:
            return False
        
        win_title_lower = win_title.lower() if win_title else ""
        
        # Step 1: Is this process in the focus apps list?
        is_focus_app = any(
            focus.replace('.exe', '') in proc_name
            for focus in self._focus_apps
        )

        if not is_focus_app:
            return False

        # Step 2: If it's a browser AND we have tab keywords, check the title
        if self._is_browser(proc_name) and self._focus_tabs:
            return any(kw in win_title_lower for kw in self._focus_tabs)

        # Step 3: Non-browser focus app, or browser with no tab filter → focused
        return True

    # ------------------------------------------------------------------
    # Core loop
    # ------------------------------------------------------------------

    def _is_browser(self, proc_name: str) -> bool:
        """Returns True if the process is a known web browser."""
        return proc_name in BROWSER_PROCESSES

    def _monitor_loop(self):
        """Runs every second to check if the user is staying on task."""
        _tick_count = 0
        while self._is_running:
            time.sleep(1)
            self.total_seconds += 1
            _tick_count += 1

            proc_name, win_title = self._get_foreground_info()

            if proc_name:
                is_focusing = self.check_focus(proc_name, win_title)

                # Debug log every 10 seconds for browser apps
                if _tick_count % 10 == 0 and self._is_browser(proc_name) and self._focus_tabs:
                    short_title = (win_title[:80] + '...') if len(win_title) > 80 else win_title
                    print(f"[Monitor] Tick {_tick_count}: {proc_name} | title=\"{short_title}\" | focused={is_focusing}")

                # Update counters
                if is_focusing:
                    self.focus_seconds += 1
                    # Per-app breakdown
                    self.app_focus_times[proc_name] = self.app_focus_times.get(proc_name, 0) + 1
                    self._was_focusing_last_tick = True
                else:
                    if self._was_focusing_last_tick:
                        self.distractions += 1
                        distraction_detail = f"{proc_name}"
                        if self._is_browser(proc_name) and win_title:
                            short = win_title[:60]
                            distraction_detail = f"{proc_name} -> {short}"
                        print(f"[Monitor] Distraction! -> {distraction_detail}")
                    self._was_focusing_last_tick = False