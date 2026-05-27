from datetime import datetime
from typing import Optional, Tuple
import pytz

class HelperManager:

    @staticmethod
    def decimal_to_probability(decimal_odds: float) -> float:
        """Convert decimal odds to implied probability"""
        return 1 / decimal_odds
    
    @staticmethod
    def convert_to_est(utc_time_str: str) -> Tuple[Optional[datetime], str]:
        """
        Convert UTC time string to EST
        
        Returns:
            Tuple of (EST datetime object, formatted EST time string)
        """
        try:
            # Parse UTC time (API returns ISO 8601 format)
            utc_dt = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
            if utc_dt.tzinfo is None:
                utc_dt = pytz.UTC.localize(utc_dt)
            
            # Convert to EST
            est = pytz.timezone('US/Eastern')
            est_dt = utc_dt.astimezone(est)
            
            # Format for display
            formatted_time = est_dt.strftime("%Y-%m-%d %I:%M %p EST")
            
            return est_dt, formatted_time
        except Exception as e:
            print(f"Error converting time: {e}")
            return None, utc_time_str
    
    @staticmethod
    def is_game_live(commence_time_str: str, max_game_duration_hours: float = 4.0) -> bool:
        """
        Determine if a game is currently live
        
        Args:
            commence_time_str: UTC time string from API
            max_game_duration_hours: Maximum expected game duration in hours
            
        Returns:
            True if game is live, False if upcoming or completed
        """
        try:
            est_dt, _ = HelperManager.convert_to_est(commence_time_str)
            if est_dt is None:
                return False
            
            now_est = datetime.now(pytz.timezone('US/Eastern'))
            time_diff = (now_est - est_dt).total_seconds() / 3600  # Convert to hours
            
            # Game is live if it has started but hasn't exceeded max duration
            return 0 <= time_diff <= max_game_duration_hours
        except Exception as e:
            return False
