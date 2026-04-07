"""
Database Manager Module
Handles the connection and initialization of the SQLite database.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "lockin.db")

def get_connection():
    """Returns a connection to the SQLite database."""
    # Enable foreign keys for SQLite
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initializes the database and creates all required tables from the Design Document."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        profile_picture BLOB,
        bio TEXT
    )
    """)
    
    # 2. Sessions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP,
        focus_time_seconds INTEGER DEFAULT 0,
        distraction_count INTEGER DEFAULT 0,
        description VARCHAR(255),
        status VARCHAR(20) DEFAULT 'active',
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    )
    """)

    # 3. Activities Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Activities (
        activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        active_window VARCHAR(255),
        application_name VARCHAR(100),
        is_distraction BOOLEAN,
        FOREIGN KEY (session_id) REFERENCES Sessions(session_id)
    )
    """)

    # 4. DistractionList Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DistractionList (
        distraction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        application_name VARCHAR(100),
        url_pattern VARCHAR(255),
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    )
    """)

    # 5. Competitions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Competitions (
        competition_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        creator_id INTEGER NOT NULL,
        start_date TIMESTAMP NOT NULL,
        end_date TIMESTAMP NOT NULL,
        status VARCHAR(20) DEFAULT 'active',
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (creator_id) REFERENCES Users(user_id)
    )
    """)

    # 6. CompetitionParticipants Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS CompetitionParticipants (
        participant_id INTEGER PRIMARY KEY AUTOINCREMENT,
        competition_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        total_focus_time_seconds INTEGER DEFAULT 0,
        rank INTEGER,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (competition_id) REFERENCES Competitions(competition_id),
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        UNIQUE(competition_id, user_id)
    )
    """)

    # 7. UserStats Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS UserStats (
        stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total_sessions INTEGER DEFAULT 0,
        total_focus_time_seconds INTEGER DEFAULT 0,
        total_distractions INTEGER DEFAULT 0,
        average_session_length_seconds INTEGER DEFAULT 0,
        best_session_seconds INTEGER DEFAULT 0,
        current_streak_days INTEGER DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    )
    """)
    
    conn.commit()
    conn.close()
    print(f"[Database] Successfully generated all tables at: {DB_PATH}")

def create_initial_user_stats(user_id: int):
    """Creates a blank stats row for a newly registered user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO UserStats (user_id) VALUES (?)
    """, (user_id,))
    conn.commit()
    conn.close()

def get_user_stats(user_id: int) -> dict:
    """Fetches the user's current stats from the database as a dictionary."""
    conn = get_connection()
    # Row factory allows us to access columns by name instead of index!
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM UserStats WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def update_user_stats(user_id: int, new_stats: dict):
    """Saves the freshly calculated stats back to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE UserStats 
        SET total_sessions = ?, 
            total_focus_time_seconds = ?, 
            total_distractions = ?, 
            average_session_length_seconds = ?, 
            best_session_seconds = ?,
            last_updated = CURRENT_TIMESTAMP
        WHERE user_id = ?
    """, (
        new_stats['total_sessions'],
        new_stats['total_focus_time_seconds'],
        new_stats['total_distractions'],
        new_stats['average_session_length_seconds'],
        new_stats['best_session_seconds'],
        user_id
    ))
    conn.commit()
    conn.close()

def reset_db():
    """Deletes the existing database file and creates a fresh one."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"[Database] Deleted old database at {DB_PATH}")
    else:
        print("[Database] No existing database found.")
        
    init_db()
    print("[Database] Fresh database successfully generated!")
    

if __name__ == "__main__":
    init_db()