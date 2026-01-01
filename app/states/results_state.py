import reflex as rx
from .base_state import State
from app.services.statistics_service import StatisticsService
import logging
import datetime


class ResultsState(State):
    user_calculations: list[dict] = []
    selected_type_filter: str = "all"
    is_loading: bool = False
    detail_modal_open: bool = False
    selected_calculation: dict = {}
    formatted_input_data: list[dict[str, str]] = []
    formatted_output_data: list[dict[str, str]] = []
    selected_ids: list[str] = []
    is_anonymizing: bool = False
    show_confirm_dialog: bool = False

    def _format_data_list(self, data: dict, prefix: str = "") -> list[dict[str, str]]:
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
    def open_detail_modal(self, calc: dict):
        self.selected_calculation = calc
        self.formatted_input_data = self._format_data_list(calc.get("input_data", {}))
        self.formatted_output_data = self._format_data_list(calc.get("output_data", {}))
        self.detail_modal_open = True

    @rx.event
    def close_detail_modal(self):
        self.detail_modal_open = False

    @rx.event
    def load_user_results(self):
        if not self.is_authenticated or not self.user:
            return
        self.is_loading = True
        self.selected_ids = []
        try:
            user_id = self.user.get("id")
            if user_id:
                self.user_calculations = StatisticsService.get_user_calculations(
                    user_id
                )
        except Exception as e:
            logging.exception(f"Error loading user results: {e}")
            rx.toast.error("Kon resultaten niet laden.")
        finally:
            self.is_loading = False

    @rx.event
    def toggle_selection(self, calc_id: str):
        if calc_id in self.selected_ids:
            self.selected_ids.remove(calc_id)
        else:
            self.selected_ids.append(calc_id)

    @rx.event
    def toggle_select_all(self):
        filtered_ids = [str(c.get("id")) for c in self.filtered_calculations]
        if len(self.selected_ids) >= len(filtered_ids) and len(filtered_ids) > 0:
            self.selected_ids = []
        else:
            self.selected_ids = filtered_ids

    @rx.var
    def all_selected(self) -> bool:
        filtered_ids = [str(c.get("id")) for c in self.filtered_calculations]
        return len(filtered_ids) > 0 and len(self.selected_ids) >= len(filtered_ids)

    @rx.var
    def has_selection(self) -> bool:
        return len(self.selected_ids) > 0

    @rx.event
    def open_confirm_dialog(self):
        if not self.has_selection:
            return rx.toast.warning("Selecteer eerst resultaten om te verwijderen.")
        self.show_confirm_dialog = True

    @rx.event
    def close_confirm_dialog(self):
        self.show_confirm_dialog = False

    @rx.event
    async def anonymize_selected(self):
        if not self.selected_ids:
            return
        self.is_anonymizing = True
        self.show_confirm_dialog = False
        yield
        try:
            success = StatisticsService.anonymize_calculations(self.selected_ids)
            if success:
                yield rx.toast.success(
                    f"{len(self.selected_ids)} resultaten succesvol geanonimiseerd."
                )
                yield ResultsState.load_user_results
            else:
                yield rx.toast.error("Er is een fout opgetreden bij het anonimiseren.")
        except Exception as e:
            logging.exception(f"Anonymization failed: {e}")
            yield rx.toast.error("Fout bij het verwerken van uw verzoek.")
        finally:
            self.is_anonymizing = False

    @rx.event
    def set_type_filter(self, value: str):
        self.selected_type_filter = value

    @rx.var
    def filtered_calculations(self) -> list[dict]:
        if self.selected_type_filter == "all":
            return self.user_calculations
        return [
            c
            for c in self.user_calculations
            if c.get("calculator_type") == self.selected_type_filter
        ]

    @rx.var
    def type_counts(self) -> dict[str, int]:
        counts = {"all": len(self.user_calculations)}
        for c in self.user_calculations:
            ctype = c.get("calculator_type", "unknown")
            counts[ctype] = counts.get(ctype, 0) + 1
        return counts

    @rx.var
    def has_results(self) -> bool:
        return len(self.user_calculations) > 0