"""
Stats Engine (v2)
Handles all business logic for calculating and updating user statistics.
"""

from datetime import datetime, date


class StatsEngine:

    @staticmethod
    def calculate_focus_score(focus_time_seconds: int,
                               total_time_seconds: int,
                               distraction_count: int) -> float:
        """
        Calculates a focus score from 0-100 based on:
          - Focus ratio (70% weight): how much of the session was focused
          - Distraction penalty (30% weight): penalises frequent distractions
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
        """Converts seconds to HH:MM:SS string."""
        if not seconds or seconds < 0:
            return "00:00:00"
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    @staticmethod
    def calculate_updated_totals(current_stats: dict, session_data: dict) -> dict:
        """
        Merges a new session into the existing UserStats dict.
        Returns the updated stats dict (does not write to DB).
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
