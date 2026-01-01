import reflex as rx
import json
import datetime
from app.services.rate_limit_service import RateLimitService
import logging


class RateLimitState(rx.State):
    usage_cookie: str = rx.Cookie(name="energie_insight_usage", max_age=31536000)

    def _get_usage_data(self) -> dict:
        if not self.usage_cookie:
            return {}
        try:
            return json.loads(self.usage_cookie)
        except json.JSONDecodeError as e:
            logging.exception(f"Error decoding usage cookie: {e}")
            return {}

    def _save_usage_data(self, data: dict):
        self.usage_cookie = json.dumps(data)

    def _get_today_str(self) -> str:
        return datetime.date.today().isoformat()

    @rx.event
    def check_can_execute(self, module_name: str) -> bool:
        """
        Check if the user can execute the given module based on rate limits.
        Checks strictly against daily and total limits retrieved from RateLimitService.
        """
        is_auth = getattr(self, "is_authenticated", False)
        limits = RateLimitService.get_limits(is_auth)
        data = self._get_usage_data()
        module_data = data.get(module_name, {})
        today_str = self._get_today_str()
        stored_date = module_data.get("date", today_str)
        current_daily = module_data.get("today", 0)
        if stored_date != today_str:
            current_daily = 0
        current_total = module_data.get("total", 0)
        if current_daily >= limits["daily"]:
            logging.warning(f"Rate limit exceeded (daily) for {module_name}")
            return False
        if current_total >= limits["total"]:
            logging.warning(f"Rate limit exceeded (total) for {module_name}")
            return False
        return True

    @rx.event
    def increment_usage(self, module_name: str):
        """
        Increment the usage counter for the given module.
        Updates the cookie with new counts and current date.
        """
        data = self._get_usage_data()
        today_str = self._get_today_str()
        if module_name not in data:
            data[module_name] = {"today": 0, "total": 0, "date": today_str}
        module_data = data[module_name]
        if module_data.get("date") != today_str:
            module_data["today"] = 0
            module_data["date"] = today_str
        module_data["today"] += 1
        module_data["total"] += 1
        self._save_usage_data(data)

    @rx.event
    def get_remaining_uses(self, module_name: str) -> dict[str, int]:
        """
        Get remaining uses for today and total based on current cookies and environment limits.
        """
        is_auth = getattr(self, "is_authenticated", False)
        limits = RateLimitService.get_limits(is_auth)
        data = self._get_usage_data()
        module_data = data.get(module_name, {})
        today_str = self._get_today_str()
        stored_date = module_data.get("date", today_str)
        current_daily = module_data.get("today", 0)
        if stored_date != today_str:
            current_daily = 0
        current_total = module_data.get("total", 0)
        return {
            "daily": max(0, limits["daily"] - current_daily),
            "total": max(0, limits["total"] - current_total),
        }

    @rx.event
    def get_usage_status(self, module_name: str) -> str:
        """
        Returns a human readable status string using the shared service formatter.
        """
        remaining = self.get_remaining_uses(module_name)
        return RateLimitService.format_usage_status(
            remaining["daily"], remaining["total"]
        )