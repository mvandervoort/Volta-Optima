import reflex as rx
from app.services.supabase_client import supabase
import logging
from datetime import datetime, timedelta
from typing import Optional


class StatisticsService:
    TABLE_NAME = "calculation_stats"

    @staticmethod
    def get_client_ip(state: rx.State) -> str:
        """
        Extracts the client IP address from the Reflex session data.
        """
        try:
            if state and state.router and state.router.session:
                client_ip = state.router.session.client_ip
                if client_ip:
                    return client_ip
        except Exception as e:
            logging.exception(f"Error extracting client IP: {e}")
        return "unknown"

    @staticmethod
    def track_calculation(
        state: rx.State,
        calculator_type: str,
        input_data: dict[str, object],
        output_data: dict[str, object],
    ) -> bool:
        """
        Records a calculation event in the database.

        Args:
            state: The current Reflex state instance (to access user info and headers)
            calculator_type: The type of calculation (e.g., 'solar_yield', 'warm_water')
            input_data: Dictionary of inputs provided by the user
            output_data: Dictionary of calculation results
        """
        if not supabase:
            logging.warning("Supabase client not initialized. Cannot track statistics.")
            return False
        try:
            user_id: Optional[str] = None
            user_email: Optional[str] = None
            if hasattr(state, "is_authenticated") and state.is_authenticated:
                if (
                    hasattr(state, "user")
                    and state.user
                    and isinstance(state.user, dict)
                ):
                    user_id = state.user.get("id")
                    user_email = state.user.get("email")
            ip_address = StatisticsService.get_client_ip(state)
            session_id = (
                state.router.session.client_token
                if state.router and state.router.session
                else None
            )
            record = {
                "calculator_type": calculator_type,
                "input_data": input_data,
                "output_data": output_data,
                "ip_address": ip_address,
                "user_id": user_id,
                "user_email": user_email,
                "session_id": session_id,
            }
            response = (
                supabase.table(StatisticsService.TABLE_NAME).insert(record).execute()
            )
            if response and hasattr(response, "data") and response.data:
                logging.info(
                    f"Successfully tracked {calculator_type} calculation for {user_email or 'anonymous'}."
                )
                return True
            return False
        except Exception as e:
            logging.exception(f"Failed to track calculation statistics: {e}")
            return False

    @staticmethod
    def get_total_calculation_count() -> int:
        """Get total number of calculations performed."""
        if not supabase:
            return 0
        try:
            response = (
                supabase.table(StatisticsService.TABLE_NAME)
                .select("*", count="exact", head=True)
                .execute()
            )
            return response.count or 0
        except Exception as e:
            logging.exception(f"Error fetching total calculation count: {e}")
            return 0

    @staticmethod
    def get_calculations_by_type() -> list[dict[str, object]]:
        """Get distribution of calculations by type."""
        if not supabase:
            return []
        try:
            response = (
                supabase.table(StatisticsService.TABLE_NAME)
                .select("calculator_type")
                .execute()
            )
            if not response.data:
                return []
            counts = {}
            for item in response.data:
                ctype = item.get("calculator_type", "unknown")
                counts[ctype] = counts.get(ctype, 0) + 1
            return [{"type": k, "value": v} for k, v in counts.items()]
        except Exception as e:
            logging.exception(f"Error fetching calculations by type: {e}")
            return []

    @staticmethod
    def get_user_stats() -> dict[str, int]:
        """Get counts of anonymous vs logged-in users."""
        if not supabase:
            return {"anonymous": 0, "logged_in": 0}
        try:
            anon_resp = (
                supabase.table(StatisticsService.TABLE_NAME)
                .select("*", count="exact", head=True)
                .is_("user_id", "null")
                .execute()
            )
            anon_count = anon_resp.count or 0
            auth_resp = (
                supabase.table(StatisticsService.TABLE_NAME)
                .select("*", count="exact", head=True)
                .not_.is_("user_id", "null")
                .execute()
            )
            auth_count = auth_resp.count or 0
            return {"anonymous": anon_count, "logged_in": auth_count}
        except Exception as e:
            logging.exception(f"Error fetching user stats: {e}")
            return {"anonymous": 0, "logged_in": 0}

    @staticmethod
    def get_recent_calculations(
        limit: int = 10, calculator_type: Optional[str] = None
    ) -> list[dict[str, object]]:
        """Get the most recent calculations."""
        if not supabase:
            return []
        try:
            query = (
                supabase.table(StatisticsService.TABLE_NAME)
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
            )
            if calculator_type and calculator_type != "all":
                query = query.eq("calculator_type", calculator_type)
            response = query.execute()
            return response.data or []
        except Exception as e:
            logging.exception(f"Error fetching recent calculations: {e}")
            return []

    @staticmethod
    def get_calculations_over_time(
        days: int = 30, calculator_type: Optional[str] = None
    ) -> list[dict[str, object]]:
        """Get daily calculation counts for the last N days."""
        if not supabase:
            return []
        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            query = (
                supabase.table(StatisticsService.TABLE_NAME)
                .select("created_at, calculator_type")
                .gte("created_at", start_date)
            )
            if calculator_type and calculator_type != "all":
                query = query.eq("calculator_type", calculator_type)
            response = query.execute()
            if not response.data:
                return []
            daily_counts = {}
            now = datetime.now()
            for i in range(days):
                d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
                daily_counts[d] = 0
            for item in response.data:
                created_at = item.get("created_at")
                if created_at:
                    date_str = created_at.split("T")[0]
                    if date_str in daily_counts:
                        daily_counts[date_str] += 1
            result = [{"date": k, "count": v} for k, v in sorted(daily_counts.items())]
            return result
        except Exception as e:
            logging.exception(f"Error fetching calculations over time: {e}")
            return []

    @staticmethod
    def get_user_calculations(user_id: str, limit: int = 50) -> list[dict[str, object]]:
        """Get calculations for a specific user."""
        if not supabase:
            return []
        try:
            response = (
                supabase.table(StatisticsService.TABLE_NAME)
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data or []
        except Exception as e:
            logging.exception(f"Error fetching user calculations: {e}")
            return []

    @staticmethod
    def anonymize_calculations(calculation_ids: list[str]) -> bool:
        """
        Removes the user association from the specified calculations.
        This anonymizes the data by setting user_id and user_email to None.
        """
        if not supabase:
            return False
        try:
            response = (
                supabase.table(StatisticsService.TABLE_NAME)
                .update({"user_id": None, "user_email": None})
                .in_("id", calculation_ids)
                .execute()
            )
            return bool(response.data)
        except Exception as e:
            logging.exception(f"Error anonymizing calculations: {e}")
            return False