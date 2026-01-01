import os
import logging


class RateLimitService:
    """
    Service to handle rate limit configurations via environment variables.

    Environment Variables:
    - ADVICE_LIMIT_PER_DAY: Max advice requests per day (default: 5)
    - ADVICE_LIMIT_TOTAL: Max lifetime advice requests (default: 50)
    - ADVICE_LIMIT_LOGGED_IN_MULTIPLIER: Multiplier for authenticated users (default: 2)
    """

    @staticmethod
    def get_daily_limit() -> int:
        try:
            return int(os.getenv("ADVICE_LIMIT_PER_DAY", "5"))
        except ValueError as e:
            logging.exception(f"Error parsing ADVICE_LIMIT_PER_DAY: {e}")
            return 5

    @staticmethod
    def get_total_limit() -> int:
        try:
            return int(os.getenv("ADVICE_LIMIT_TOTAL", "50"))
        except ValueError as e:
            logging.exception(f"Error parsing ADVICE_LIMIT_TOTAL: {e}")
            return 50

    @staticmethod
    def get_logged_in_multiplier() -> int:
        try:
            return int(os.getenv("ADVICE_LIMIT_LOGGED_IN_MULTIPLIER", "2"))
        except ValueError as e:
            logging.exception(f"Error parsing ADVICE_LIMIT_LOGGED_IN_MULTIPLIER: {e}")
            return 2

    @staticmethod
    def get_limits(is_authenticated: bool) -> dict[str, int]:
        """
        Calculate effective limits based on authentication status.
        Returns a dict with 'daily' and 'total' integer limits.
        """
        multiplier = (
            RateLimitService.get_logged_in_multiplier() if is_authenticated else 1
        )
        return {
            "daily": RateLimitService.get_daily_limit() * multiplier,
            "total": RateLimitService.get_total_limit() * multiplier,
        }

    @staticmethod
    def format_usage_status(daily_left: int, total_left: int) -> str:
        """
        Returns a formatted string for UI display of remaining usage.
        """
        return f"Resterend vandaag: {daily_left} | Totaal over: {total_left}"