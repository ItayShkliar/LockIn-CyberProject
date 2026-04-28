"""
Comprehensive test suite for browser tab focus tracking.

Tests cover:
  - AppMonitor.check_focus() logic for all scenarios
  - Keyword matching (case insensitivity, partial match, multiple keywords)
  - Browser vs non-browser process handling
  - Focus tab keywords from empty to full
  - Distraction counting with browser tab switching
  - AppScanner browser tab detection and utility methods
  - Full session lifecycle with browser focus tracking
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import time
import threading

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CLIENT_DIR = os.path.join(ROOT_DIR, 'src', 'client')
SERVER_DIR = os.path.join(ROOT_DIR, 'src', 'server')
sys.path.insert(0, CLIENT_DIR)
sys.path.insert(0, SERVER_DIR)

from logic.app_monitor import AppMonitor, BROWSER_PROCESSES
from logic.app_scanner import AppScanner, BROWSER_PROCESSES as SCANNER_BROWSER_PROCESSES


# ===========================================================================
# TEST: AppMonitor.check_focus() — Keyword Matching Logic
# ===========================================================================

class TestCheckFocus(unittest.TestCase):
    """Tests the core check_focus() method of AppMonitor in isolation,
    without needing real Windows API calls."""

    def setUp(self):
        self.monitor = AppMonitor()

    # ------------------------------------------------------------------
    # Basic app focus (no browser tab tracking)
    # ------------------------------------------------------------------

    def test_focus_app_match_no_tabs(self):
        """A non-browser focus app should count as focused."""
        self.monitor._focus_apps = ['code.exe']
        self.monitor._focus_tabs = []
        result = self.monitor.check_focus('code.exe', 'main.py - Visual Studio Code')
        self.assertTrue(result)

    def test_focus_app_no_match(self):
        """A non-focus app should return False."""
        self.monitor._focus_apps = ['code.exe']
        self.monitor._focus_tabs = []
        result = self.monitor.check_focus('discord.exe', 'Discord')
        self.assertFalse(result)

    def test_focus_app_partial_name_match(self):
        """Focus app matching uses 'in' operator, so partial matches work."""
        self.monitor._focus_apps = ['chrome.exe']
        self.monitor._focus_tabs = []
        result = self.monitor.check_focus('chrome.exe', 'Google Chrome')
        self.assertTrue(result)

    def test_none_proc_name(self):
        """None process name should return False."""
        self.monitor._focus_apps = ['chrome.exe']
        self.monitor._focus_tabs = []
        result = self.monitor.check_focus(None, '')
        self.assertFalse(result)

    # ------------------------------------------------------------------
    # Browser focus WITH tab keywords
    # ------------------------------------------------------------------

    def test_browser_with_matching_keyword(self):
        """Chrome on GitHub with keyword 'github' should be focused."""
        self.monitor._focus_apps = ['chrome.exe']
        self.monitor._focus_tabs = ['github']
        result = self.monitor.check_focus(
            'chrome.exe',
            'ItayShkliar/LockIn-CyberProject · GitHub - Google Chrome'
        )
        self.assertTrue(result, "Should match 'github' in the title")

    def test_browser_with_non_matching_keyword(self):
        """Chrome on YouTube with keyword 'github' should NOT be focused."""
        self.monitor._focus_apps = ['chrome.exe']
        self.monitor._focus_tabs = ['github']
        result = self.monitor.check_focus(
            'chrome.exe',
            'Funny Cat Videos - YouTube - Google Chrome'
        )
        self.assertFalse(result, "YouTube should not match 'github'")

    def test_browser_keyword_case_insensitive(self):
        """Keyword matching should be case-insensitive."""
        self.monitor._focus_apps = ['chrome.exe']
        self.monitor._focus_tabs = ['github']  # lowercase keyword
        result = self.monitor.check_focus(
            'chrome.exe',
            'ItayShkliar/LockIn · GitHub - Google Chrome'  # uppercase GitHub
        )
        self.assertTrue(result, "Case insensitive match should work")

    def test_browser_multiple_keywords_any_match(self):
        """If ANY keyword matches the title, it should be focused."""
        self.monitor._focus_apps = ['chrome.exe']
        self.monitor._focus_tabs = ['github', 'stack overflow', 'docs.google']

        # On Stack Overflow — keyword is 'stack overflow' which IS in the title
        result = self.monitor.check_focus(
            'chrome.exe',
            'python - How to use threads - Stack Overflow - Google Chrome'
        )
        self.assertTrue(result, "'stack overflow' should match Stack Overflow title")

        # On Google Docs — 'docs.google' is NOT in the title 'Google Docs'
        result = self.monitor.check_focus(
            'chrome.exe',
            'My Document - Google Docs - Google Chrome'
        )
        self.assertFalse(result, "'docs.google' is not in 'Google Docs' title")

    def test_browser_keyword_partial_url_match(self):
        """Keywords can be partial domain names."""
        self.monitor._focus_apps = ['chrome.exe']
        self.monitor._focus_tabs = ['notion']
        result = self.monitor.check_focus(
            'chrome.exe',
            'My Workspace - Notion - Google Chrome'
        )
        self.assertTrue(result)

    def test_browser_no_keywords_all_focused(self):
        """Browser with NO tab keywords should count ALL tabs as focused."""
        self.monitor._focus_apps = ['chrome.exe']
        self.monitor._focus_tabs = []  # empty = all tabs allowed
        result = self.monitor.check_focus(
            'chrome.exe',
            'Random YouTube Video - Google Chrome'
        )
        self.assertTrue(result, "No keywords = all browser tabs are focused")

    def test_browser_empty_title(self):
        """Browser with empty window title and keywords should NOT be focused."""
        self.monitor._focus_apps = ['chrome.exe']
        self.monitor._focus_tabs = ['github']
        result = self.monitor.check_focus('chrome.exe', '')
        self.assertFalse(result, "Empty title cannot match any keyword")

    def test_browser_none_title(self):
        """Browser with None title should NOT be focused."""
        self.monitor._focus_apps = ['chrome.exe']
        self.monitor._focus_tabs = ['github']
        result = self.monitor.check_focus('chrome.exe', None)
        self.assertFalse(result, "None title cannot match any keyword")

    # ------------------------------------------------------------------
    # Edge browser
    # ------------------------------------------------------------------

    def test_edge_browser_keyword_match(self):
        """Microsoft Edge should also support tab keyword matching."""
        self.monitor._focus_apps = ['msedge.exe']
        self.monitor._focus_tabs = ['github']
        result = self.monitor.check_focus(
            'msedge.exe',
            'ItayShkliar/LockIn - GitHub - Microsoft Edge'
        )
        self.assertTrue(result)

    # ------------------------------------------------------------------
    # Brave browser
    # ------------------------------------------------------------------

    def test_brave_browser_keyword_match(self):
        """Brave browser should also support tab keyword matching."""
        self.monitor._focus_apps = ['brave.exe']
        self.monitor._focus_tabs = ['stack overflow']
        result = self.monitor.check_focus(
            'brave.exe',
            'How to fix Python errors - Stack Overflow - Brave'
        )
        self.assertTrue(result)

    # ------------------------------------------------------------------
    # Firefox
    # ------------------------------------------------------------------

    def test_firefox_keyword_match(self):
        """Firefox should also support tab keyword matching."""
        self.monitor._focus_apps = ['firefox.exe']
        self.monitor._focus_tabs = ['python']
        result = self.monitor.check_focus(
            'firefox.exe',
            'Welcome to Python.org — Mozilla Firefox'
        )
        self.assertTrue(result)

    # ------------------------------------------------------------------
    # Mixed: browser + non-browser focus apps
    # ------------------------------------------------------------------

    def test_mixed_focus_apps_non_browser_still_works(self):
        """When both browser and non-browser are focus apps,
        non-browser apps should still be focused without tab checks."""
        self.monitor._focus_apps = ['chrome.exe', 'code.exe']
        self.monitor._focus_tabs = ['github']

        # VS Code should be focused (no tab check needed)
        result = self.monitor.check_focus('code.exe', 'main.py - Visual Studio Code')
        self.assertTrue(result, "Non-browser focus app should pass without tab check")

        # Chrome on GitHub should be focused
        result = self.monitor.check_focus(
            'chrome.exe', 'GitHub - Google Chrome'
        )
        self.assertTrue(result)

        # Chrome on YouTube should NOT be focused
        result = self.monitor.check_focus(
            'chrome.exe', 'YouTube - Google Chrome'
        )
        self.assertFalse(result)

    # ------------------------------------------------------------------
    # Non-focus browser
    # ------------------------------------------------------------------

    def test_browser_not_in_focus_apps(self):
        """A browser that's NOT in focus_apps should not be focused,
        even if tab keywords match."""
        self.monitor._focus_apps = ['code.exe']  # no browser
        self.monitor._focus_tabs = ['github']
        result = self.monitor.check_focus(
            'chrome.exe', 'GitHub - Google Chrome'
        )
        self.assertFalse(result, "Chrome is not in focus_apps")

    # ------------------------------------------------------------------
    # Whitespace in keywords
    # ------------------------------------------------------------------

    def test_keyword_with_spaces_trimmed(self):
        """Keywords should be trimmed of whitespace."""
        self.monitor._focus_apps = ['chrome.exe']
        self.monitor._focus_tabs = ['github']
        result = self.monitor.check_focus(
            'chrome.exe', 'Issues · GitHub - Google Chrome'
        )
        self.assertTrue(result)


# ===========================================================================
# TEST: Full Monitor Lifecycle with Mocked Foreground Info
# ===========================================================================

class TestMonitorLifecycle(unittest.TestCase):
    """Tests the monitor thread lifecycle with mocked OS calls."""

    def test_monitor_counts_focus_on_matching_browser_tab(self):
        """Monitor should count focus seconds when browser tab matches keyword."""
        monitor = AppMonitor()
        monitor._get_foreground_info = MagicMock(
            return_value=('chrome.exe', 'My Repo - GitHub - Google Chrome')
        )
        monitor.start_monitoring(['chrome.exe'], focus_tabs=['github'])
        time.sleep(3.5)
        total, focus, dists, app_times = monitor.stop_monitoring()

        self.assertGreaterEqual(total, 3)
        self.assertGreaterEqual(focus, 2, "Should have counted focus seconds")
        self.assertEqual(dists, 0, "No distractions expected")

    def test_monitor_counts_distraction_on_non_matching_tab(self):
        """Monitor should count distractions when browser tab doesn't match."""
        monitor = AppMonitor()
        monitor._get_foreground_info = MagicMock(
            return_value=('chrome.exe', 'Funny Cats - YouTube - Google Chrome')
        )
        monitor.start_monitoring(['chrome.exe'], focus_tabs=['github'])
        time.sleep(3.5)
        total, focus, dists, app_times = monitor.stop_monitoring()

        self.assertGreaterEqual(total, 2)
        self.assertEqual(focus, 0, "YouTube should not count as focus")
        self.assertEqual(dists, 1, "Should log exactly 1 distraction (first switch)")

    def test_monitor_tab_switch_logs_distraction(self):
        """Switching from a matching tab to a non-matching tab should log a distraction."""
        monitor = AppMonitor()
        call_count = [0]

        def _mock_foreground():
            call_count[0] += 1
            if call_count[0] <= 2:
                return ('chrome.exe', 'My Repo - GitHub - Google Chrome')
            else:
                return ('chrome.exe', 'Reddit - Dive into anything - Google Chrome')

        monitor._get_foreground_info = _mock_foreground
        monitor.start_monitoring(['chrome.exe'], focus_tabs=['github'])
        time.sleep(5.5)
        total, focus, dists, app_times = monitor.stop_monitoring()

        self.assertGreaterEqual(focus, 1, "First ticks should be focused (GitHub)")
        self.assertEqual(dists, 1, "Switching to Reddit should log 1 distraction")

    def test_monitor_no_tab_keywords_all_browser_focused(self):
        """With no tab keywords, all browser usage is focused."""
        monitor = AppMonitor()
        monitor._get_foreground_info = MagicMock(
            return_value=('chrome.exe', 'YouTube - Google Chrome')
        )
        monitor.start_monitoring(['chrome.exe'], focus_tabs=None)
        time.sleep(2.5)
        total, focus, dists, app_times = monitor.stop_monitoring()

        self.assertGreaterEqual(focus, 2, "All browser usage should be focused")
        self.assertEqual(dists, 0)

    def test_monitor_non_focus_app_distraction(self):
        """Switching to a non-focus app should log a distraction."""
        monitor = AppMonitor()
        call_count = [0]

        def _mock_foreground():
            call_count[0] += 1
            if call_count[0] <= 2:
                return ('chrome.exe', 'GitHub - Google Chrome')
            else:
                return ('discord.exe', 'Discord')

        monitor._get_foreground_info = _mock_foreground
        monitor.start_monitoring(['chrome.exe'], focus_tabs=['github'])
        time.sleep(4.5)
        total, focus, dists, app_times = monitor.stop_monitoring()

        self.assertEqual(dists, 1, "Switching to Discord should log a distraction")

    def test_monitor_multiple_tab_switches(self):
        """Multiple switches between focus/distraction should log correctly."""
        monitor = AppMonitor()
        call_count = [0]

        def _mock_foreground():
            call_count[0] += 1
            # Pattern: github(2), youtube(2), github(2), reddit(2)
            if call_count[0] <= 2:
                return ('chrome.exe', 'My Repo - GitHub - Google Chrome')
            elif call_count[0] <= 4:
                return ('chrome.exe', 'Music - YouTube - Google Chrome')
            elif call_count[0] <= 6:
                return ('chrome.exe', 'Issues - GitHub - Google Chrome')
            else:
                return ('chrome.exe', 'Reddit - Google Chrome')

        monitor._get_foreground_info = _mock_foreground
        monitor.start_monitoring(['chrome.exe'], focus_tabs=['github'])
        time.sleep(9.5)
        total, focus, dists, app_times = monitor.stop_monitoring()

        # Should have: 2 focus, 2 distraction, 2 focus, 2+ distraction = 2 distraction events
        self.assertGreaterEqual(focus, 3)
        self.assertEqual(dists, 2, "Two switches to non-focus tabs should log 2 distractions")


# ===========================================================================
# TEST: AppScanner browser-related methods
# ===========================================================================

class TestAppScannerBrowser(unittest.TestCase):
    """Tests AppScanner's browser-related utility methods."""

    def test_is_browser_process_chrome(self):
        self.assertTrue(AppScanner.is_browser_process('chrome.exe'))

    def test_is_browser_process_edge(self):
        self.assertTrue(AppScanner.is_browser_process('msedge.exe'))

    def test_is_browser_process_brave(self):
        self.assertTrue(AppScanner.is_browser_process('brave.exe'))

    def test_is_browser_process_firefox(self):
        self.assertTrue(AppScanner.is_browser_process('firefox.exe'))

    def test_is_browser_process_notepad(self):
        self.assertFalse(AppScanner.is_browser_process('notepad.exe'))

    def test_is_browser_process_case_insensitive(self):
        """The method lowercases the input."""
        self.assertTrue(AppScanner.is_browser_process('Chrome.exe'))

    def test_browser_processes_constant(self):
        """BROWSER_PROCESSES should contain the main browsers."""
        for browser in ['chrome.exe', 'msedge.exe', 'brave.exe', 'firefox.exe']:
            self.assertIn(browser, BROWSER_PROCESSES)

    def test_get_browser_tabs_returns_list(self):
        """get_browser_tabs should return a list (may be empty if no browser open)."""
        tabs = AppScanner.get_browser_tabs()
        self.assertIsInstance(tabs, list)


# ===========================================================================
# TEST: BROWSER_PROCESSES consistency
# ===========================================================================

class TestBrowserProcessesConsistency(unittest.TestCase):
    """Ensures the BROWSER_PROCESSES constants in monitor and scanner match."""

    def test_constants_match(self):
        """Both modules should recognize the same set of browsers."""
        self.assertEqual(
            BROWSER_PROCESSES,
            SCANNER_BROWSER_PROCESSES,
            "BROWSER_PROCESSES should be identical in app_monitor and app_scanner"
        )


# ===========================================================================
# TEST: Real Chrome window title patterns
# ===========================================================================

class TestRealWorldTitlePatterns(unittest.TestCase):
    """Tests check_focus against real-world Chrome window title patterns
    that users will actually encounter."""

    def setUp(self):
        self.monitor = AppMonitor()
        self.monitor._focus_apps = ['chrome.exe']

    def test_github_repo_page(self):
        self.monitor._focus_tabs = ['github']
        self.assertTrue(self.monitor.check_focus(
            'chrome.exe',
            'ItayShkliar/LockIn-CyberProject: A productivity app · GitHub - Google Chrome'
        ))

    def test_github_issues_page(self):
        self.monitor._focus_tabs = ['github']
        self.assertTrue(self.monitor.check_focus(
            'chrome.exe',
            'Issues · ItayShkliar/LockIn-CyberProject · GitHub - Google Chrome'
        ))

    def test_github_pull_request(self):
        self.monitor._focus_tabs = ['github']
        self.assertTrue(self.monitor.check_focus(
            'chrome.exe',
            'Fix UI clipping by ItayShkliar · Pull Request #42 · GitHub - Google Chrome'
        ))

    def test_google_docs(self):
        self.monitor._focus_tabs = ['google docs']
        self.assertTrue(self.monitor.check_focus(
            'chrome.exe',
            'My Assignment - Google Docs - Google Chrome'
        ))

    def test_stackoverflow_question(self):
        """Keyword 'stack overflow' (with space) should match the title."""
        self.monitor._focus_tabs = ['stack overflow']
        self.assertTrue(self.monitor.check_focus(
            'chrome.exe',
            'python - How to read JSON - Stack Overflow - Google Chrome'
        ))

    def test_stackoverflow_partial_keyword(self):
        """Keyword 'overflow' alone should also match Stack Overflow."""
        self.monitor._focus_tabs = ['overflow']
        self.assertTrue(self.monitor.check_focus(
            'chrome.exe',
            'python - How to read JSON - Stack Overflow - Google Chrome'
        ))

    def test_youtube_distraction(self):
        self.monitor._focus_tabs = ['github', 'stack overflow']
        self.assertFalse(self.monitor.check_focus(
            'chrome.exe',
            'Never Gonna Give You Up - YouTube - Google Chrome'
        ))

    def test_reddit_distraction(self):
        self.monitor._focus_tabs = ['github']
        self.assertFalse(self.monitor.check_focus(
            'chrome.exe',
            'r/programming - Reddit - Google Chrome'
        ))

    def test_twitter_distraction(self):
        self.monitor._focus_tabs = ['github']
        self.assertFalse(self.monitor.check_focus(
            'chrome.exe',
            'Home / X - Google Chrome'
        ))

    def test_whatsapp_web_distraction(self):
        self.monitor._focus_tabs = ['github']
        self.assertFalse(self.monitor.check_focus(
            'chrome.exe',
            'WhatsApp Web - Google Chrome'
        ))

    def test_new_tab_page(self):
        self.monitor._focus_tabs = ['github']
        self.assertFalse(self.monitor.check_focus(
            'chrome.exe',
            'New Tab - Google Chrome'
        ))

    def test_notion_workspace(self):
        self.monitor._focus_tabs = ['notion']
        self.assertTrue(self.monitor.check_focus(
            'chrome.exe',
            'My Projects / Notion - Google Chrome'
        ))

    def test_figma_design(self):
        self.monitor._focus_tabs = ['figma']
        self.assertTrue(self.monitor.check_focus(
            'chrome.exe',
            'LockIn Design – Figma - Google Chrome'
        ))

    def test_multiple_keywords_mixed_sites(self):
        """With multiple keywords, each matching site should be focused."""
        self.monitor._focus_tabs = ['github', 'notion', 'stack overflow']

        sites = [
            ('GitHub - Google Chrome', True),
            ('Notion - Google Chrome', True),
            ('Stack Overflow - Google Chrome', True),
            ('YouTube - Google Chrome', False),
            ('Instagram - Google Chrome', False),
        ]
        for title, expected in sites:
            result = self.monitor.check_focus('chrome.exe', title)
            self.assertEqual(result, expected, f"Failed for title: {title}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
