"""
Database Manager (v2)
Handles all SQLite operations for the LockIn server.
New in v2:
  - Achievements table and auto-grant logic
  - Global leaderboard query
  - Competition details with participant count
  - Public competitions browser
  - Competition rank recalculation
  - Auto competition status updates
  - User profile query
"""

import sqlite3
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(__file__), "lockin.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Creates all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login    DATETIME
        );

        CREATE TABLE IF NOT EXISTS UserStats (
            stat_id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id                  INTEGER NOT NULL UNIQUE,
            total_sessions           INTEGER DEFAULT 0,
            total_focus_time_seconds INTEGER DEFAULT 0,
            total_distractions       INTEGER DEFAULT 0,
            best_session_seconds     INTEGER DEFAULT 0,
            current_streak_days      INTEGER DEFAULT 0,
            longest_streak_days      INTEGER DEFAULT 0,
            last_session_date        TEXT,
            total_score              REAL    DEFAULT 0.0,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        );

        CREATE TABLE IF NOT EXISTS Sessions (
            session_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id            INTEGER NOT NULL,
            start_time         DATETIME,
            end_time           DATETIME,
            focus_time_seconds INTEGER DEFAULT 0,
            distraction_count  INTEGER DEFAULT 0,
            description        TEXT,
            status             TEXT DEFAULT 'completed',
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        );

        CREATE TABLE IF NOT EXISTS Competitions (
            competition_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name             TEXT    NOT NULL,
            creator_id       INTEGER NOT NULL,
            start_date       DATETIME NOT NULL,
            end_date         DATETIME NOT NULL,
            description      TEXT,
            status           TEXT    DEFAULT 'pending',
            max_participants INTEGER DEFAULT 0,
            is_public        INTEGER DEFAULT 1,
            created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES Users(user_id)
        );

        CREATE TABLE IF NOT EXISTS CompetitionParticipants (
            participant_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            competition_id           INTEGER NOT NULL,
            user_id                  INTEGER NOT NULL,
            total_focus_time_seconds INTEGER DEFAULT 0,
            sessions_count           INTEGER DEFAULT 0,
            focus_score              REAL    DEFAULT 0.0,
            rank                     INTEGER,
            joined_at                DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (competition_id, user_id),
            FOREIGN KEY (competition_id) REFERENCES Competitions(competition_id),
            FOREIGN KEY (user_id)         REFERENCES Users(user_id)
        );

        CREATE TABLE IF NOT EXISTS Achievements (
            achievement_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL,
            achievement_type TEXT    NOT NULL,
            unlocked_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (user_id, achievement_type),
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        );
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")


# ---------------------------------------------------------------------------
# User stats helpers
# ---------------------------------------------------------------------------

def create_initial_user_stats(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO UserStats (user_id) VALUES (?)", (user_id,)
    )
    conn.commit()
    conn.close()


def get_user_stats(user_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM UserStats WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_stats(user_id: int, stats: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE UserStats SET
            total_sessions           = ?,
            total_focus_time_seconds = ?,
            total_distractions       = ?,
            best_session_seconds     = ?,
            current_streak_days      = ?,
            longest_streak_days      = ?,
            last_session_date        = ?,
            total_score              = ?
        WHERE user_id = ?
    """, (
        stats.get("total_sessions", 0),
        stats.get("total_focus_time_seconds", 0),
        stats.get("total_distractions", 0),
        stats.get("best_session_seconds", 0),
        stats.get("current_streak_days", 0),
        stats.get("longest_streak_days", 0),
        stats.get("last_session_date"),
        stats.get("total_score", 0.0),
        user_id,
    ))
    conn.commit()
    conn.close()


def get_user_sessions(user_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Sessions WHERE user_id = ? ORDER BY start_time DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_user_profile(user_id: int) -> dict | None:
    """Returns combined user + stats info for the profile view."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.user_id, u.username, u.email, u.created_at,
               COALESCE(s.total_sessions, 0)           AS total_sessions,
               COALESCE(s.total_focus_time_seconds, 0) AS total_focus_time_seconds,
               COALESCE(s.total_distractions, 0)       AS total_distractions,
               COALESCE(s.best_session_seconds, 0)     AS best_session_seconds,
               COALESCE(s.current_streak_days, 0)      AS current_streak_days,
               COALESCE(s.longest_streak_days, 0)      AS longest_streak_days,
               COALESCE(s.total_score, 0.0)            AS total_score
        FROM Users u
        LEFT JOIN UserStats s ON u.user_id = s.user_id
        WHERE u.user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Global leaderboard
# ---------------------------------------------------------------------------

def get_global_leaderboard(limit: int = 20) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.username,
               COALESCE(s.total_focus_time_seconds, 0) AS total_focus_time_seconds,
               COALESCE(s.total_sessions, 0)           AS total_sessions,
               COALESCE(s.best_session_seconds, 0)     AS best_session_seconds,
               COALESCE(s.current_streak_days, 0)      AS current_streak_days,
               ROW_NUMBER() OVER (
                   ORDER BY COALESCE(s.total_focus_time_seconds, 0) DESC
               ) AS rank
        FROM Users u
        LEFT JOIN UserStats s ON u.user_id = s.user_id
        ORDER BY total_focus_time_seconds DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ---------------------------------------------------------------------------
# Competition helpers
# ---------------------------------------------------------------------------

def update_competition_statuses(cursor: sqlite3.Cursor):
    """Auto-transitions competition statuses based on current datetime."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE Competitions
        SET status = 'active'
        WHERE status = 'pending' AND start_date <= ?
    """, (now,))
    cursor.execute("""
        UPDATE Competitions
        SET status = 'ended'
        WHERE status = 'active' AND end_date < ?
    """, (now,))


def recalculate_competition_ranks(competition_id: int, cursor: sqlite3.Cursor):
    """Recalculates and stores rank for all participants in a competition."""
    cursor.execute("""
        SELECT participant_id, total_focus_time_seconds
        FROM CompetitionParticipants
        WHERE competition_id = ?
        ORDER BY total_focus_time_seconds DESC
    """, (competition_id,))
    rows = cursor.fetchall()
    for rank, row in enumerate(rows, start=1):
        cursor.execute(
            "UPDATE CompetitionParticipants SET rank = ? WHERE participant_id = ?",
            (rank, row[0])
        )


def get_competition_details(competition_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*,
               u.username AS creator_name,
               COUNT(cp.user_id) AS participant_count
        FROM Competitions c
        LEFT JOIN Users u ON c.creator_id = u.user_id
        LEFT JOIN CompetitionParticipants cp ON c.competition_id = cp.competition_id
        WHERE c.competition_id = ?
        GROUP BY c.competition_id
    """, (competition_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_public_competitions() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.competition_id, c.name, c.description, c.start_date, c.end_date,
               c.status, c.max_participants,
               u.username AS creator_name,
               COUNT(cp.user_id) AS participant_count
        FROM Competitions c
        LEFT JOIN Users u ON c.creator_id = u.user_id
        LEFT JOIN CompetitionParticipants cp ON c.competition_id = cp.competition_id
        WHERE c.is_public = 1 AND c.status != 'ended'
        GROUP BY c.competition_id
        ORDER BY c.competition_id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ---------------------------------------------------------------------------
# Achievements
# ---------------------------------------------------------------------------

ACHIEVEMENT_RULES = [
    ("first_session",  lambda s: s.get("total_sessions", 0) >= 1),
    ("sessions_10",    lambda s: s.get("total_sessions", 0) >= 10),
    ("sessions_50",    lambda s: s.get("total_sessions", 0) >= 50),
    ("sessions_100",   lambda s: s.get("total_sessions", 0) >= 100),
    ("focus_1h",       lambda s: s.get("total_focus_time_seconds", 0) >= 3600),
    ("focus_10h",      lambda s: s.get("total_focus_time_seconds", 0) >= 36000),
    ("focus_100h",     lambda s: s.get("total_focus_time_seconds", 0) >= 360000),
    ("streak_3",       lambda s: s.get("current_streak_days", 0) >= 3),
    ("streak_7",       lambda s: s.get("current_streak_days", 0) >= 7),
    ("streak_30",      lambda s: s.get("current_streak_days", 0) >= 30),
]


def check_and_grant_achievements(user_id: int, stats: dict,
                                  cursor: sqlite3.Cursor) -> list[str]:
    """Checks all achievement rules and grants any newly earned ones.
    Returns a list of newly unlocked achievement type strings."""
    cursor.execute(
        "SELECT achievement_type FROM Achievements WHERE user_id = ?", (user_id,)
    )
    already_unlocked = {row[0] for row in cursor.fetchall()}
    newly_unlocked = []
    for ach_type, rule in ACHIEVEMENT_RULES:
        if ach_type not in already_unlocked and rule(stats):
            cursor.execute(
                "INSERT OR IGNORE INTO Achievements (user_id, achievement_type) VALUES (?, ?)",
                (user_id, ach_type)
            )
            newly_unlocked.append(ach_type)
            print(f"[DB] Achievement unlocked for user {user_id}: {ach_type}")
    return newly_unlocked


def get_user_achievements(user_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT achievement_type, unlocked_at FROM Achievements WHERE user_id = ? ORDER BY unlocked_at",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
