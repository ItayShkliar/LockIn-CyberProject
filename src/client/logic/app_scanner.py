"""
App Scanner Module
Scans the computer to find currently running applications.
Uses advanced filtering and keyword matching to hide background processes, 
updaters, and system services, showing only real user applications.

Also scans browser window titles to detect open tabs/sites.
"""
import psutil
import os
import ctypes

# Browser process names we recognise
BROWSER_PROCESSES = {'chrome.exe', 'msedge.exe', 'brave.exe', 'firefox.exe', 'opera.exe'}

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

    @staticmethod
    def get_browser_tabs() -> list:
        """
        Scans all visible windows for browser tabs by reading their window titles.
        Browsers show the active tab title in their window title bar.
        
        Returns:
            list: A list of tab title strings currently open in any browser.
        """
        tabs = []
        
        # Suffixes that browsers add to their window titles
        browser_suffixes = [
            ' - Google Chrome', ' - Microsoft Edge', ' - Brave',
            ' - Mozilla Firefox', ' - Opera', ' — Mozilla Firefox',
            ' - Chromium',
        ]
        
        def _enum_callback(hwnd, _):
            """Callback for EnumWindows: collects visible browser window titles."""
            if not ctypes.windll.user32.IsWindowVisible(hwnd):
                return True
            
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return True
            
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            
            for suffix in browser_suffixes:
                if title.endswith(suffix):
                    tab_title = title[: -len(suffix)]
                    if tab_title and tab_title != 'New Tab':
                        tabs.append(tab_title)
                    break
            
            return True
        
        # Define the callback type and call EnumWindows
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        ctypes.windll.user32.EnumWindows(WNDENUMPROC(_enum_callback), 0)
        
        print(f"[Scanner] Found {len(tabs)} browser tabs.")
        return sorted(set(tabs))

    @staticmethod
    def is_browser_process(process_name: str) -> bool:
        """Checks if a process name belongs to a known browser."""
        return process_name.lower() in BROWSER_PROCESSES


# ==========================================
# Test Execution Block
# ==========================================
if __name__ == "__main__":
    scanner = AppScanner()
    apps = scanner.get_running_processes()
    
    print(f"\n--- Found {len(apps)} Clean User Applications ---")
    for app in apps:
        print(f"- {app}")
    
    print(f"\n--- Browser Tabs ---")
    tabs = scanner.get_browser_tabs()
    for tab in tabs:
        print(f"  🌐 {tab}")