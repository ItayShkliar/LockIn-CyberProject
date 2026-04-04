"""
App Monitor Module
Tracks running processes and blocks (kills) distracting applications 
defined by the user during a focus session.
"""
import psutil
import time
import threading

class AppMonitor:
    """
    Class responsible for monitoring and blocking distracting applications.
    Runs in a separate thread to prevent freezing the graphical user interface.
    """
    
    def __init__(self, blocked_apps: list):
        """
        Initializes the monitoring mechanism.
        
        Args:
            blocked_apps (list): List of process names chosen by the user to block 
                                 (e.g., ['discord.exe', 'notepad.exe'])
        """
        self._blocked_apps = [app.lower() for app in blocked_apps]
        self._is_running = False
        self._distraction_count = 0
        self._monitor_thread = None

    def update_blocked_apps(self, new_blocked_apps: list):
        """
        Allows updating the blocked applications list even while the session is active.
        """
        self._blocked_apps = [app.lower() for app in new_blocked_apps]
        print(f"[Monitor] Updated blocked apps list: {self._blocked_apps}")

    def start_session(self):
        """Starts the focus session and runs the monitoring in the background."""
        if self._is_running:
            return
            
        self._is_running = True
        self._distraction_count = 0
        
        # Create a background thread to run the monitor loop
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print("[Monitor] Focus session started. Monitoring apps...")

    def stop_session(self) -> int:
        """
        Stops the focus session and returns the total number of distractions blocked.
        """
        self._is_running = False
        if self._monitor_thread:
            self._monitor_thread.join() # Wait for the thread to finish cleanly
            
        print(f"[Monitor] Session ended. Total distractions blocked: {self._distraction_count}")
        return self._distraction_count

    def _monitor_loop(self):
        """
        The main loop running in the background while the session is active.
        """
        while self._is_running:
            self._check_and_block_apps()
            # Wait 2 seconds between checks to prevent high CPU usage
            time.sleep(2) 

    def _check_and_block_apps(self):
        """
        Checks running processes and blocks those in the blacklist.
        Counts each unique app only ONCE per scan cycle, even if the app 
        uses multiple background processes (like Discord or Chrome).
        """
        # Use a Set to keep track of unique apps we blocked in this specific loop cycle
        apps_blocked_this_cycle = set()

        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                
                # If the application is in the user's blacklist
                if proc_name in self._blocked_apps:
                    proc.kill() # Block the app by killing the process
                    apps_blocked_this_cycle.add(proc_name) # Add to our tracking set
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Handle cases where the process closes before we can act, or we lack permissions
                pass
        
        # After scanning all processes, update the distraction count and print logs
        for app in apps_blocked_this_cycle:
            print(f"[Monitor] Distraction detected! Blocked: {app}")
            self._distraction_count += 1

# ==========================================
# Test Execution Block
# ==========================================
if __name__ == "__main__":
    # Change this to an app you want to test (e.g., 'notepad.exe')
    user_chosen_apps = ["notepad.exe"] 
    
    monitor = AppMonitor(user_chosen_apps)
    monitor.start_session()
    
    print(f"Try opening a blocked app ({user_chosen_apps[0]})... it should close immediately!")
    print("Press Ctrl+C to stop.")
    
    try:
        # Let the session run for 15 seconds for testing purposes
        time.sleep(15)
    except KeyboardInterrupt:
        pass
    finally:
        total_distractions = monitor.stop_session()
        print(f"Test finished. Total distractions blocked: {total_distractions}")