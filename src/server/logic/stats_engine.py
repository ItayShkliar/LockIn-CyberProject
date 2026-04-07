"""
Stats Engine Module
Centralizes all mathematical formulas for user stats and leaderboards.
"""

class StatsEngine:
    
    @staticmethod
    def get_default_stats(user_id: int) -> dict:
        """Returns the default, blank stats profile for a brand new user."""
        return {
            "user_id": user_id,
            "total_sessions": 0,
            "total_focus_time_seconds": 0,
            "total_distractions": 0,
            "average_session_length_seconds": 0,
            "best_session_seconds": 0,
            "current_streak_days": 0
        }

    @staticmethod
    def calculate_updated_totals(current_stats: dict, session_data: dict) -> dict:
        """
        Takes the user's current database stats, adds the new session data, 
        and calculates the new averages and maximums.
        """
        focus_time = session_data.get('focus_time_seconds', 0)
        distractions = session_data.get('distraction_count', 0)

        new_total_sessions = current_stats['total_sessions'] + 1
        new_total_focus = current_stats['total_focus_time_seconds'] + focus_time
        new_total_distractions = current_stats['total_distractions'] + distractions

        # Check if this was their best session yet!
        new_best = max(current_stats['best_session_seconds'], focus_time)

        # Calculate the new average focus time
        new_avg = new_total_focus // new_total_sessions if new_total_sessions > 0 else 0

        return {
            "total_sessions": new_total_sessions,
            "total_focus_time_seconds": new_total_focus,
            "total_distractions": new_total_distractions,
            "average_session_length_seconds": new_avg,
            "best_session_seconds": new_best,
            "current_streak_days": current_stats['current_streak_days'] # Streaks will be calculated daily
        }