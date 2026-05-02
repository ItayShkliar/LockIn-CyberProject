"""
Stats Engine Module

This module handles all business logic for calculating and updating user statistics.
It processes session data, calculates focus scores, handles streak logic, and formats durations.
"""

from datetime import datetime, date


class StatsEngine:
    """
    A utility class containing static methods for statistical calculations.
    It processes focus sessions and determines performance metrics without directly
    interacting with the database, ensuring clean separation of concerns.
    """

    @staticmethod
    def calculate_focus_score(focus_time_seconds: int,
                               total_time_seconds: int,
                               distraction_count: int) -> float:
        """
        Calculates a focus score from 0-100 based on session performance.

        The score is heavily weighted towards the focus ratio (70%) and applies a 
        penalty for frequent distractions (30%).

        Args:
            focus_time_seconds (int): Total seconds spent explicitly focused.
            total_time_seconds (int): Total duration of the session in seconds.
            distraction_count (int): Number of times the user switched to a blocked application.

        Returns:
            float: The calculated focus score (0.0 to 100.0).
        """
        if total_time_seconds <= 0:
            return 0.0

        focus_ratio = min(focus_time_seconds / total_time_seconds, 1.0)
        focus_component = focus_ratio * 70.0

        # Distraction penalty: 5 points per distraction, capped at 30
        distraction_penalty = min(distraction_count * 5, 30)
        distraction_component = 30.0 - distraction_penalty

        score = focus_component + distraction_component
        return round(max(0.0, min(100.0, score)), 2)

    @staticmethod
    def format_duration(seconds: int) -> str:
        """
        Converts a duration in seconds to a formatted HH:MM:SS string.

        Args:
            seconds (int): The total number of seconds.

        Returns:
            str: The formatted time string (e.g., '01:30:15').
        """
        if not seconds or seconds < 0:
            return "00:00:00"
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    @staticmethod
    def calculate_updated_totals(current_stats: dict, session_data: dict) -> dict:
        """
        Merges a new session's data into an existing user's statistics dictionary.
        
        It recalculates total sessions, time, distractions, updates the all-time 
        best session, manages the rolling average focus score, and calculates streaks 
        based on the last session date.

        Args:
            current_stats (dict): The user's current statistics from the database.
            session_data (dict): The data from the newly completed focus session.

        Returns:
            dict: A new dictionary containing the updated statistics.
        """
        updated = dict(current_stats)

        focus_time = session_data.get("focus_time_seconds", 0)
        distractions = session_data.get("distraction_count", 0)
        total_time = session_data.get("total_time_seconds", focus_time)

        # Increment counters
        updated["total_sessions"] = current_stats.get("total_sessions", 0) + 1
        updated["total_focus_time_seconds"] = (
            current_stats.get("total_focus_time_seconds", 0) + focus_time
        )
        updated["total_distractions"] = (
            current_stats.get("total_distractions", 0) + distractions
        )

        # Best session
        if focus_time > current_stats.get("best_session_seconds", 0):
            updated["best_session_seconds"] = focus_time

        # Rolling average focus score
        session_score = StatsEngine.calculate_focus_score(
            focus_time, total_time, distractions
        )
        n = updated["total_sessions"]
        old_score = current_stats.get("total_score", 0.0)
        updated["total_score"] = round(
            (old_score * (n - 1) + session_score) / n, 2
        )

        # Streak calculation
        today_str = date.today().isoformat()
        last_date_str = current_stats.get("last_session_date")
        current_streak = current_stats.get("current_streak_days", 0)
        longest_streak = current_stats.get("longest_streak_days", 0)

        if last_date_str:
            try:
                last_date = date.fromisoformat(last_date_str)
                delta = (date.today() - last_date).days
                if delta == 0:
                    # Same day — streak unchanged
                    pass
                elif delta == 1:
                    # Consecutive day — extend streak
                    current_streak += 1
                else:
                    # Streak broken
                    current_streak = 1
            except (ValueError, TypeError):
                current_streak = 1
        else:
            current_streak = 1

        longest_streak = max(longest_streak, current_streak)
        updated["current_streak_days"] = current_streak
        updated["longest_streak_days"] = longest_streak
        updated["last_session_date"] = today_str

        return updated
