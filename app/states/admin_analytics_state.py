import reflex as rx
from app.services.statistics_service import StatisticsService
import datetime
import logging


class AdminAnalyticsState(rx.State):
    total_calculations: int = 0
    calculations_by_type: list[dict] = []
    calculations_over_time: list[dict] = []
    recent_calculations: list[dict] = []
    anon_count: int = 0
    logged_in_count: int = 0
    calculations_this_week_count: int = 0
    most_popular_calculator: str = "-"
    selected_date_range: str = "30"
    selected_calc_type: str = "all"
    is_loading: bool = False
    detail_modal_open: bool = False
    selected_stat: dict = {}
    formatted_input_data: list[dict[str, str]] = []
    formatted_output_data: list[dict[str, str]] = []

    def _format_data_list(self, data: dict, prefix: str = "") -> list[dict[str, str]]:
        """Helper to flatten and format JSON data for display."""
        if not data or not isinstance(data, dict):
            return []
        result = []
        for k, v in data.items():
            clean_key = k.replace("_", " ").title()
            label = f"{prefix}{clean_key}" if prefix else clean_key
            if isinstance(v, dict):
                result.extend(self._format_data_list(v, prefix=f"{label} - "))
            else:
                val_str = str(v)
                if isinstance(v, bool):
                    val_str = "Ja" if v else "Nee"
                elif isinstance(v, float):
                    val_str = (
                        f"{v:,.2f}".replace(",", "_")
                        .replace(".", ",")
                        .replace("_", ".")
                    )
                elif v is None:
                    val_str = "-"
                result.append({"label": label, "value": val_str})
        return result

    @rx.event
    def open_detail_modal(self, stat: dict):
        self.selected_stat = stat
        self.formatted_input_data = self._format_data_list(stat.get("input_data", {}))
        self.formatted_output_data = self._format_data_list(stat.get("output_data", {}))
        self.detail_modal_open = True

    @rx.event
    def close_detail_modal(self):
        self.detail_modal_open = False

    @rx.event
    async def load_analytics(self):
        self.is_loading = True
        yield
        try:
            self.total_calculations = StatisticsService.get_total_calculation_count()
            self.calculations_by_type = StatisticsService.get_calculations_by_type()
            days = int(self.selected_date_range)
            self.calculations_over_time = StatisticsService.get_calculations_over_time(
                days=days, calculator_type=self.selected_calc_type
            )
            self.recent_calculations = StatisticsService.get_recent_calculations(
                limit=20, calculator_type=self.selected_calc_type
            )
            user_stats = StatisticsService.get_user_stats()
            self.anon_count = user_stats.get("anonymous", 0)
            self.logged_in_count = user_stats.get("logged_in", 0)
            today = datetime.date.today()
            week_ago = today - datetime.timedelta(days=7)
            week_count = 0
            for item in self.calculations_over_time:
                d_str = item["date"]
                d = datetime.date.fromisoformat(d_str)
                if d >= week_ago:
                    week_count += item["count"]
            self.calculations_this_week_count = week_count
            if self.calculations_by_type:
                sorted_types = sorted(
                    self.calculations_by_type, key=lambda x: x["value"], reverse=True
                )
                if sorted_types:
                    self.most_popular_calculator = (
                        sorted_types[0]["type"].replace("_", " ").title()
                    )
        except Exception as e:
            logging.exception(f"Error loading analytics: {e}")
        finally:
            self.is_loading = False

    @rx.event
    def set_date_range(self, value: str):
        self.selected_date_range = value
        return AdminAnalyticsState.load_analytics

    @rx.event
    def set_calc_type(self, value: str):
        self.selected_calc_type = value
        return AdminAnalyticsState.load_analytics