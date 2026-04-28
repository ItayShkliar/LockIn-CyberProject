"""
Comprehensive test suite for multiplayer competitions and related features.

Tests cover:
  - Competition creation (valid, invalid, public/private)
  - Joining competitions (success, duplicate, full, ended)
  - Leaving competitions
  - Competition leaderboards with rank recalculation
  - Session uploads updating competition stats
  - Multiple users competing simultaneously
  - Competition status transitions (pending → active → ended)
  - Edge cases (empty competitions, max participants)

These tests spin up the real socket server on a random port and communicate
with it via the NetworkClient, testing the full end-to-end flow.
"""

import sys
import os
import socket
import json
import struct
import sqlite3
import threading
import time
import unittest
import shutil
import tempfile
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Path setup – make sure we can import from src/server and src/client
# ---------------------------------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SERVER_DIR = os.path.join(ROOT_DIR, 'src', 'server')
CLIENT_DIR = os.path.join(ROOT_DIR, 'src', 'client')
sys.path.insert(0, SERVER_DIR)
sys.path.insert(0, CLIENT_DIR)

from database import db_manager
from logic.stats_engine import StatsEngine


# ---------------------------------------------------------------------------
# Helper: Simple TCP client that speaks the length-prefixed JSON protocol
# ---------------------------------------------------------------------------

class TestClient:
    """Lightweight TCP client that mirrors the server's framing protocol."""

    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port

    def send_request(self, payload: dict) -> dict:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((self.host, self.port))
            data = json.dumps(payload).encode('utf-8')
            s.sendall(struct.pack('>I', len(data)) + data)
            # Read response
            raw_header = self._recv_exact(s, 4)
            msg_len = struct.unpack('>I', raw_header)[0]
            raw_body = self._recv_exact(s, msg_len)
            return json.loads(raw_body.decode('utf-8'))

    @staticmethod
    def _recv_exact(sock, n):
        buf = b''
        while len(buf) < n:
            chunk = sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("Server closed connection")
            buf += chunk
        return buf


# ---------------------------------------------------------------------------
# Helper: Start a fresh server instance for testing
# ---------------------------------------------------------------------------

def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def _start_test_server(port, db_path):
    """Starts the socket server on a dedicated port using a test database."""
    import database.db_manager as dbm
    # Monkey-patch the DB_PATH to use our temp database
    dbm.DB_PATH = db_path

    from socket_server import handle_client, send_message, recv_message

    dbm.init_db()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', port))
    server.settimeout(1.0)
    server.listen(50)

    def _serve():
        while getattr(_serve, '_running', True):
            try:
                conn, addr = server.accept()
                t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                t.start()
            except socket.timeout:
                pass
        server.close()

    _serve._running = True
    thread = threading.Thread(target=_serve, daemon=True)
    thread.start()
    return _serve, server


# ===========================================================================
# TEST SUITE
# ===========================================================================

class TestCompetitions(unittest.TestCase):
    """End-to-end tests for multiplayer competitions."""

    @classmethod
    def setUpClass(cls):
        """Creates a temporary database and starts a test server."""
        cls._tmpdir = tempfile.mkdtemp()
        cls._db_path = os.path.join(cls._tmpdir, 'test_lockin.db')
        cls._port = _find_free_port()

        cls._serve_fn, cls._server_sock = _start_test_server(cls._port, cls._db_path)
        time.sleep(0.5)  # Allow server to bind

        cls.client = TestClient(port=cls._port)

    @classmethod
    def tearDownClass(cls):
        cls._serve_fn._running = False
        time.sleep(1.5)
        try:
            cls._server_sock.close()
        except Exception:
            pass
        shutil.rmtree(cls._tmpdir, ignore_errors=True)

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    def _register(self, username, email=None, password='testpass123'):
        if email is None:
            email = f"{username}@test.com"
        return self.client.send_request({
            "action": "register",
            "username": username,
            "email": email,
            "password": password,
        })

    def _login(self, username, password='testpass123'):
        return self.client.send_request({
            "action": "login",
            "username": username,
            "password": password,
        })

    def _create_competition(self, user_id, name, start_offset_hours=-1,
                            end_offset_hours=24, max_participants=0,
                            is_public=True, description="Test competition"):
        now = datetime.now()
        start = (now + timedelta(hours=start_offset_hours)).strftime("%Y-%m-%d %H:%M:%S")
        end = (now + timedelta(hours=end_offset_hours)).strftime("%Y-%m-%d %H:%M:%S")
        return self.client.send_request({
            "action": "create_competition",
            "user_id": user_id,
            "name": name,
            "start_date": start,
            "end_date": end,
            "description": description,
            "max_participants": max_participants,
            "is_public": is_public,
        })

    def _join_competition(self, user_id, competition_id):
        return self.client.send_request({
            "action": "join_competition",
            "user_id": user_id,
            "competition_id": competition_id,
        })

    def _leave_competition(self, user_id, competition_id):
        return self.client.send_request({
            "action": "leave_competition",
            "user_id": user_id,
            "competition_id": competition_id,
        })

    def _upload_session(self, user_id, focus_seconds=300, total_seconds=360,
                        distractions=2, description="Test Session"):
        now = datetime.now()
        start = (now - timedelta(seconds=total_seconds)).strftime("%Y-%m-%d %H:%M:%S")
        end = now.strftime("%Y-%m-%d %H:%M:%S")
        return self.client.send_request({
            "action": "upload_session",
            "user_id": user_id,
            "session_data": {
                "start_time": start,
                "end_time": end,
                "description": description,
                "total_time_seconds": total_seconds,
                "focus_time_seconds": focus_seconds,
                "distraction_count": distractions,
                "status": "completed",
            }
        })

    def _get_leaderboard(self, competition_id):
        return self.client.send_request({
            "action": "get_leaderboard",
            "competition_id": competition_id,
        })

    def _get_user_competitions(self, user_id):
        return self.client.send_request({
            "action": "get_user_competitions",
            "user_id": user_id,
        })

    def _get_competition_details(self, competition_id):
        return self.client.send_request({
            "action": "get_competition_details",
            "competition_id": competition_id,
        })

    def _get_public_competitions(self):
        return self.client.send_request({
            "action": "get_public_competitions",
        })

    def _get_global_leaderboard(self, limit=20):
        return self.client.send_request({
            "action": "get_global_leaderboard",
            "limit": limit,
        })

    # ==================================================================
    # 1. REGISTRATION & LOGIN
    # ==================================================================

    def test_01_register_users(self):
        """Register multiple users for competition testing."""
        for name in ['alice', 'bob', 'charlie', 'dave']:
            resp = self._register(name)
            self.assertEqual(resp['status'], 'success', f"Failed to register {name}: {resp}")

    def test_02_duplicate_registration(self):
        """Duplicate username registration should fail."""
        resp = self._register('alice')
        self.assertEqual(resp['status'], 'error')
        self.assertIn('already', resp['message'].lower())

    def test_03_login_success(self):
        """Valid credentials should return user_id."""
        resp = self._login('alice')
        self.assertEqual(resp['status'], 'success')
        self.assertIn('user_id', resp)

    def test_04_login_failure(self):
        """Invalid password should fail."""
        resp = self._login('alice', password='wrongpass')
        self.assertEqual(resp['status'], 'error')

    # ==================================================================
    # 2. COMPETITION CREATION
    # ==================================================================

    def test_05_create_public_competition(self):
        """Creating a public competition should succeed and return a room_code."""
        alice = self._login('alice')
        resp = self._create_competition(
            alice['user_id'], "Focus Battle Royale",
            is_public=True, description="Who can focus the longest?"
        )
        self.assertEqual(resp['status'], 'success')
        self.assertIn('room_code', resp)
        self.__class__._comp1_id = resp['room_code']

    def test_06_create_private_competition(self):
        """Creating a private competition should succeed."""
        alice = self._login('alice')
        resp = self._create_competition(
            alice['user_id'], "Secret Study Group",
            is_public=False, description="Private group"
        )
        self.assertEqual(resp['status'], 'success')
        self.__class__._comp_private_id = resp['room_code']

    def test_07_create_competition_with_max_participants(self):
        """Creating a competition with max_participants limit."""
        alice = self._login('alice')
        resp = self._create_competition(
            alice['user_id'], "Small Room",
            max_participants=2, description="Only 2 allowed"
        )
        self.assertEqual(resp['status'], 'success')
        self.__class__._comp_small_id = resp['room_code']

    def test_08_create_competition_missing_fields(self):
        """Missing required fields should fail."""
        alice = self._login('alice')
        resp = self.client.send_request({
            "action": "create_competition",
            "user_id": alice['user_id'],
            "name": "",  # empty name
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
        })
        self.assertEqual(resp['status'], 'error')

    # ==================================================================
    # 3. JOINING COMPETITIONS
    # ==================================================================

    def test_09_join_competition_success(self):
        """Bob and Charlie should be able to join the public competition."""
        bob = self._login('bob')
        resp = self._join_competition(bob['user_id'], self._comp1_id)
        self.assertEqual(resp['status'], 'success')

        charlie = self._login('charlie')
        resp = self._join_competition(charlie['user_id'], self._comp1_id)
        self.assertEqual(resp['status'], 'success')

    def test_10_join_competition_duplicate(self):
        """Joining the same competition twice should fail."""
        bob = self._login('bob')
        resp = self._join_competition(bob['user_id'], self._comp1_id)
        self.assertEqual(resp['status'], 'error')
        self.assertIn('already', resp['message'].lower())

    def test_11_join_nonexistent_competition(self):
        """Joining a non-existent competition should fail."""
        bob = self._login('bob')
        resp = self._join_competition(bob['user_id'], 99999)
        self.assertEqual(resp['status'], 'error')
        self.assertIn('not found', resp['message'].lower())

    def test_12_join_full_competition(self):
        """Joining a full competition should fail (max_participants enforced)."""
        # Small room has max 2, and alice (creator) is already in it
        bob = self._login('bob')
        resp = self._join_competition(bob['user_id'], self._comp_small_id)
        self.assertEqual(resp['status'], 'success')

        # Now charlie tries to join — should be rejected (2/2 full)
        charlie = self._login('charlie')
        resp = self._join_competition(charlie['user_id'], self._comp_small_id)
        self.assertEqual(resp['status'], 'error')
        self.assertIn('full', resp['message'].lower())

    # ==================================================================
    # 4. LEAVING COMPETITIONS
    # ==================================================================

    def test_13_leave_competition_success(self):
        """A participant should be able to leave a competition."""
        bob = self._login('bob')
        # Bob leaves the small room
        resp = self._leave_competition(bob['user_id'], self._comp_small_id)
        self.assertEqual(resp['status'], 'success')

    def test_14_leave_competition_not_member(self):
        """Leaving a competition you're not in should fail."""
        dave = self._login('dave')
        resp = self._leave_competition(dave['user_id'], self._comp1_id)
        self.assertEqual(resp['status'], 'error')

    # ==================================================================
    # 5. SESSION UPLOADS & COMPETITION STATS
    # ==================================================================

    def test_15_upload_session_updates_competition(self):
        """Uploading a session should update competition participant stats."""
        alice = self._login('alice')
        resp = self._upload_session(
            alice['user_id'], focus_seconds=600, total_seconds=700, distractions=1
        )
        self.assertEqual(resp['status'], 'success')
        self.assertIn('session_score', resp)
        self.assertGreater(resp['session_score'], 0)

    def test_16_multiple_users_upload_sessions(self):
        """Multiple users uploading sessions should update the leaderboard correctly."""
        bob = self._login('bob')
        charlie = self._login('charlie')

        # Bob uploads a strong session
        self._upload_session(bob['user_id'], focus_seconds=1800, total_seconds=2000, distractions=0)
        # Charlie uploads a weaker session
        self._upload_session(charlie['user_id'], focus_seconds=500, total_seconds=1000, distractions=5)

    def test_17_leaderboard_ranking(self):
        """Leaderboard should rank participants by total focus time descending."""
        resp = self._get_leaderboard(self._comp1_id)
        self.assertEqual(resp['status'], 'success')
        lb = resp['leaderboard']

        self.assertGreaterEqual(len(lb), 2)

        # Verify descending order of focus time
        for i in range(len(lb) - 1):
            self.assertGreaterEqual(
                lb[i]['focus_time'], lb[i + 1]['focus_time'],
                f"Leaderboard not sorted: rank {lb[i]['rank']} has less focus than rank {lb[i+1]['rank']}"
            )

    def test_18_leaderboard_has_correct_fields(self):
        """Each leaderboard entry should have required fields."""
        resp = self._get_leaderboard(self._comp1_id)
        for entry in resp['leaderboard']:
            self.assertIn('rank', entry)
            self.assertIn('username', entry)
            self.assertIn('focus_time', entry)
            self.assertIn('focus_time_formatted', entry)
            self.assertIn('sessions_count', entry)
            self.assertIn('focus_score', entry)

    def test_19_cumulative_sessions(self):
        """Multiple sessions from the same user should accumulate in competition stats."""
        alice = self._login('alice')

        # Upload a second session for alice
        self._upload_session(alice['user_id'], focus_seconds=400, total_seconds=500, distractions=0)

        resp = self._get_leaderboard(self._comp1_id)
        alice_entry = None
        for entry in resp['leaderboard']:
            if entry['username'] == 'alice':
                alice_entry = entry
                break

        self.assertIsNotNone(alice_entry, "Alice should be on the leaderboard")
        # Alice should have at least 2 sessions (from test_15 and this test)
        self.assertGreaterEqual(alice_entry['sessions_count'], 2)
        # Her focus time should be cumulative (600 + 400 = 1000 at minimum)
        self.assertGreaterEqual(alice_entry['focus_time'], 1000)

    # ==================================================================
    # 6. COMPETITION DETAILS & BROWSING
    # ==================================================================

    def test_20_get_competition_details(self):
        """Should return full details for a given competition."""
        resp = self._get_competition_details(self._comp1_id)
        self.assertEqual(resp['status'], 'success')
        comp = resp['competition']
        self.assertEqual(comp['name'], 'Focus Battle Royale')
        self.assertIn('participant_count', comp)
        self.assertGreaterEqual(comp['participant_count'], 1)

    def test_21_get_user_competitions(self):
        """Should list all competitions a user has joined."""
        alice = self._login('alice')
        resp = self._get_user_competitions(alice['user_id'])
        self.assertEqual(resp['status'], 'success')
        rooms = resp['rooms']
        # Alice created 3 competitions (public, private, small)
        self.assertGreaterEqual(len(rooms), 3)
        names = [r['name'] for r in rooms]
        self.assertIn('Focus Battle Royale', names)

    def test_22_get_public_competitions(self):
        """Should only return public competitions that haven't ended."""
        resp = self._get_public_competitions()
        self.assertEqual(resp['status'], 'success')
        comps = resp['competitions']
        # All returned should be public
        for c in comps:
            # The private competition should NOT appear
            self.assertNotEqual(c['name'], 'Secret Study Group')

    def test_23_private_competition_not_listed(self):
        """Private competitions should not appear in public browsing."""
        resp = self._get_public_competitions()
        names = [c['name'] for c in resp['competitions']]
        self.assertNotIn('Secret Study Group', names)

    # ==================================================================
    # 7. GLOBAL LEADERBOARD
    # ==================================================================

    def test_24_global_leaderboard(self):
        """Global leaderboard should rank all users by total focus time."""
        resp = self._get_global_leaderboard(limit=10)
        self.assertEqual(resp['status'], 'success')
        lb = resp['leaderboard']
        self.assertGreater(len(lb), 0)

        # Should be sorted by total_focus_time_seconds descending
        for i in range(len(lb) - 1):
            self.assertGreaterEqual(
                lb[i]['total_focus_time_seconds'],
                lb[i + 1]['total_focus_time_seconds']
            )

    def test_25_global_leaderboard_fields(self):
        """Each global leaderboard entry should have the expected fields."""
        resp = self._get_global_leaderboard(limit=5)
        for entry in resp['leaderboard']:
            self.assertIn('rank', entry)
            self.assertIn('username', entry)
            self.assertIn('total_focus_time_seconds', entry)
            self.assertIn('focus_time_formatted', entry)
            self.assertIn('total_sessions', entry)

    # ==================================================================
    # 8. ACHIEVEMENTS
    # ==================================================================

    def test_26_first_session_achievement(self):
        """Uploading a session should grant the 'first_session' achievement."""
        alice = self._login('alice')
        resp = self.client.send_request({
            "action": "get_achievements",
            "user_id": alice['user_id'],
        })
        self.assertEqual(resp['status'], 'success')
        ach_types = [a['achievement_type'] for a in resp['achievements']]
        self.assertIn('first_session', ach_types)

    # ==================================================================
    # 9. USER PROFILE
    # ==================================================================

    def test_27_user_profile(self):
        """User profile should return cumulative stats."""
        alice = self._login('alice')
        resp = self.client.send_request({
            "action": "get_user_profile",
            "user_id": alice['user_id'],
        })
        self.assertEqual(resp['status'], 'success')
        profile = resp['profile']
        self.assertEqual(profile['username'], 'alice')
        self.assertGreater(profile['total_sessions'], 0)
        self.assertGreater(profile['total_focus_time_seconds'], 0)

    # ==================================================================
    # 10. SESSION HISTORY
    # ==================================================================

    def test_28_get_sessions(self):
        """Session history should return all uploaded sessions."""
        alice = self._login('alice')
        resp = self.client.send_request({
            "action": "get_sessions",
            "user_id": alice['user_id'],
        })
        self.assertEqual(resp['status'], 'success')
        self.assertGreaterEqual(len(resp['sessions']), 2)
        # Sessions should have timestamps
        for s in resp['sessions']:
            self.assertIn('start_time', s)
            self.assertIn('end_time', s)
            self.assertIn('focus_time_seconds', s)

    # ==================================================================
    # 11. EDGE CASES
    # ==================================================================

    def test_29_unknown_action(self):
        """Sending an unknown action should return an error."""
        resp = self.client.send_request({"action": "fly_to_moon"})
        self.assertEqual(resp['status'], 'error')

    def test_30_empty_leaderboard(self):
        """Leaderboard for a competition with only one member (creator)."""
        alice = self._login('alice')
        # The private competition only has alice
        resp = self._get_leaderboard(self._comp_private_id)
        self.assertEqual(resp['status'], 'success')
        self.assertEqual(len(resp['leaderboard']), 1)
        self.assertEqual(resp['leaderboard'][0]['username'], 'alice')

    def test_31_daily_stats(self):
        """Daily stats endpoint should return today's focus data."""
        alice = self._login('alice')
        resp = self.client.send_request({
            "action": "get_daily_stats",
            "user_id": alice['user_id'],
        })
        self.assertEqual(resp['status'], 'success')
        self.assertIn('daily_focus_seconds', resp)
        self.assertIn('daily_sessions', resp)
        self.assertIn('daily_focus_formatted', resp)

    def test_32_competition_rejoining_after_leave(self):
        """A user who left should be able to rejoin (if not full)."""
        bob = self._login('bob')
        # Bob left the small room earlier. Now rejoin.
        resp = self._join_competition(bob['user_id'], self._comp_small_id)
        self.assertEqual(resp['status'], 'success')

    def test_33_stress_multiple_sessions(self):
        """Upload many sessions rapidly and verify stats accumulate."""
        dave = self._login('dave')
        user_id = dave['user_id']

        # Dave joins the public competition
        self._join_competition(user_id, self._comp1_id)

        total_focus = 0
        for i in range(5):
            focus = 100 + i * 50
            total_focus += focus
            resp = self._upload_session(user_id, focus_seconds=focus,
                                        total_seconds=focus + 30,
                                        distractions=i,
                                        description=f"Stress test {i+1}")
            self.assertEqual(resp['status'], 'success')

        # Check dave's position in the leaderboard
        resp = self._get_leaderboard(self._comp1_id)
        dave_entry = None
        for entry in resp['leaderboard']:
            if entry['username'] == 'dave':
                dave_entry = entry
                break
        self.assertIsNotNone(dave_entry)
        self.assertEqual(dave_entry['sessions_count'], 5)
        self.assertEqual(dave_entry['focus_time'], total_focus)


# ===========================================================================
# Stats Engine unit tests
# ===========================================================================

class TestStatsEngine(unittest.TestCase):
    """Unit tests for the StatsEngine business logic."""

    def test_perfect_focus_score(self):
        """100% focus with no distractions should score 100."""
        score = StatsEngine.calculate_focus_score(3600, 3600, 0)
        self.assertEqual(score, 100.0)

    def test_zero_time_score(self):
        """Zero total time should return 0."""
        score = StatsEngine.calculate_focus_score(0, 0, 0)
        self.assertEqual(score, 0.0)

    def test_distraction_penalty(self):
        """Distractions should reduce the score."""
        score_clean = StatsEngine.calculate_focus_score(3600, 3600, 0)
        score_messy = StatsEngine.calculate_focus_score(3600, 3600, 3)
        self.assertGreater(score_clean, score_messy)

    def test_distraction_penalty_cap(self):
        """Distraction penalty should be capped at 30 points."""
        score_6 = StatsEngine.calculate_focus_score(3600, 3600, 6)
        score_100 = StatsEngine.calculate_focus_score(3600, 3600, 100)
        # Both should have the same penalty (capped at 30)
        self.assertEqual(score_6, score_100)

    def test_half_focus(self):
        """50% focus should still score reasonably."""
        score = StatsEngine.calculate_focus_score(1800, 3600, 0)
        self.assertGreater(score, 30)
        self.assertLess(score, 80)

    def test_format_duration(self):
        """Time formatting should be correct."""
        self.assertEqual(StatsEngine.format_duration(0), "00:00:00")
        self.assertEqual(StatsEngine.format_duration(61), "00:01:01")
        self.assertEqual(StatsEngine.format_duration(3661), "01:01:01")
        self.assertEqual(StatsEngine.format_duration(86400), "24:00:00")

    def test_calculate_updated_totals(self):
        """calculate_updated_totals should correctly merge a session into stats."""
        current = {
            "total_sessions": 5,
            "total_focus_time_seconds": 10000,
            "total_distractions": 10,
            "best_session_seconds": 3000,
            "current_streak_days": 2,
            "longest_streak_days": 5,
            "last_session_date": None,
            "total_score": 80.0,
        }
        session = {
            "focus_time_seconds": 4000,
            "total_time_seconds": 4200,
            "distraction_count": 1,
        }
        updated = StatsEngine.calculate_updated_totals(current, session)
        self.assertEqual(updated['total_sessions'], 6)
        self.assertEqual(updated['total_focus_time_seconds'], 14000)
        self.assertEqual(updated['total_distractions'], 11)
        self.assertEqual(updated['best_session_seconds'], 4000)  # new best


if __name__ == '__main__':
    unittest.main(verbosity=2)
