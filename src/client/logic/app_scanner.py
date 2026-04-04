"""
App Scanner Module
Scans the computer to find currently running applications.
Uses advanced filtering and keyword matching to hide background processes, 
updaters, and system services, showing only real user applications.
"""
import psutil
import os

class AppScanner:
    """
    A utility class to discover user-facing applications currently running on the PC.
    """
    
    @staticmethod
    def get_running_processes() -> list:
        """
        Retrieves a highly filtered list of running process names.
        
        Returns:
            list: A sorted list of unique, user-facing process names.
        """
        running_apps = set()
        current_user = os.environ.get('USERNAME', '').lower()
        
        # Exact names of background apps we want to ignore
        exact_ignore_list = [
            'explorer.exe', 'cmd.exe', 'conhost.exe', 'taskmgr.exe', 
            'searchapp.exe', 'startmenuexperiencehost.exe', 'widgets.exe',
            'ctfmon.exe', 'sihost.exe', 'runtimebroker.exe',
            'searchhost.exe', 'applicationframehost.exe', 'systemsettings.exe',
            'textinputhost.exe', 'securityhealthsystray.exe', 'smartscreen.exe',
            'cortana.exe', 'appvshnotify.exe', 'cclibrary.exe', 'ccxprocess.exe',
            'iastoricon.exe', 'rtkuwp.exe', 'jucheck.exe', 'jusched.exe',
            'node.exe', 'python.exe', 'python3.12.exe' # Usually background dev environments
        ]

        # Keywords: If the .exe contains any of these words, it's a background process
        ignore_keywords = [
            'helper', 'crash', 'broker', 'service', 'container', 
            'webview', 'setup', 'notification', 'agent', 'cache', 
            'update', 'host', 'sync', 'tray'
        ]
        
        print("[Scanner] Scanning PC for real user applications...")
        
        for proc in psutil.process_iter(['name', 'username', 'exe']):
            try:
                proc_name = proc.info['name'].lower()
                proc_user = proc.info['username']
                exe_path = proc.info['exe']
                
                # Filter 1: Must belong to the current user
                if not (proc_user and current_user in proc_user.lower()):
                    continue
                    
                # Filter 2: Ignore core Windows paths
                if not exe_path or 'c:\\windows' in exe_path.lower():
                    continue
                    
                # Filter 3: Exact name match ignore list
                if proc_name in exact_ignore_list:
                    continue
                    
                # Filter 4: Keyword matching (e.g. catches 'msedgewebview2.exe' or 'discord_helper.exe')
                if any(keyword in proc_name for keyword in ignore_keywords):
                    continue
                    
                # If it passed all filters, it's likely a real app!
                running_apps.add(proc_name)
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        return sorted(list(running_apps))

# ==========================================
# Test Execution Block
# ==========================================
if __name__ == "__main__":
    scanner = AppScanner()
    apps = scanner.get_running_processes()
    
    print(f"\n--- Found {len(apps)} Clean User Applications ---")
    
    for app in apps:
        print(f"- {app}")