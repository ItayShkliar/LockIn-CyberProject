"""
App Scanner Module
Scans the computer to find currently running applications.
This helps the user select the exact process names (e.g., 'discord.exe') to block.
"""
import psutil

class AppScanner:
    """
    A utility class to discover applications currently running on the PC.
    """
    
    @staticmethod
    def get_running_processes() -> list:
        """
        Retrieves a list of all currently running process names on the PC.
        
        Returns:
            list: A sorted list of unique process names (in lowercase).
        """
        running_apps = set()
        
        print("[Scanner] Scanning PC for running applications...")
        
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name']
                if proc_name:
                    # Add to set to prevent duplicates, save as lowercase
                    running_apps.add(proc_name.lower())
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Skip processes that we don't have permission to read or that just closed
                pass
                
        # Return as a sorted list alphabetically
        return sorted(list(running_apps))

# ==========================================
# Test Execution Block
# ==========================================
if __name__ == "__main__":
    scanner = AppScanner()
    apps = scanner.get_running_processes()
    
    print(f"\n--- Found {len(apps)} Running Processes ---")
    
    # Print the first 50 processes just to show how it works
    for app in apps[:50]:
        print(f"- {app}")
        
    print("\n[Tip] Look through this list to find the EXACT name of the app you want to block.")