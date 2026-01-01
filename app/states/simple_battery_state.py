import reflex as rx
import logging
from .base_state import State
from app.services.email_service import EmailService
from app.services.statistics_service import StatisticsService
import datetime


class SimpleBatteryState(State):
    annual_consumption: float = 3500.0
    annual_grid_import: float = 1500.0
    eta: float = 0.9
    dod: float = 0.8
    safety_factor: float = 1.15
    show_advanced_params: bool = False
    electricity_price: float = 0.25
    battery_cost_per_kwh: float = 700.0
    has_calculated: bool = False
    is_processing: bool = False
    optimal_capacity: float = 0.0
    avg_daily_export: float = 0.0
    usable_capacity: float = 0.0
    extra_self_consumption: float = 0.0
    percent_offset: float = 0.0
    annual_savings: float = 0.0
    total_battery_cost: float = 0.0
    payback_period: float = 0.0
    roi: float = 0.0
    is_sending_email: bool = False
    email_sent_modal_open: bool = False
    intro_content: dict[str, str] = {
        "title": "Eenvoudige Batterij Berekening",
        "subtitle": "Bereken snel de optimale batterijgrootte voor uw situatie.",
        "instructions": """
        <p>Deze calculator helpt u een eerste inschatting te maken van de ideale thuisbatterij voor uw woning. Op basis van uw verbruikspatroon en zonne-installatie berekenen we de optimale opslagcapaciteit.</p>
        <p class="mt-4"><strong>Het principe van Energy Shifting:</strong></p>
        <p class="mt-2">Een thuisbatterij werkt op het principe van <em>energy shifting</em>: energie die u overdag opwekt met zonnepanelen wordt opgeslagen en 's avonds gebruikt wanneer u het nodig heeft.</p>
        """,
    }
    technical_details_content: dict[str, str] = {
        "title": "Technische Achtergrond & Aannames",
        "content": """
        <h3 class="text-lg font-semibold text-gray-800 mb-2">Berekeningsmethodiek</h3>
        <p class="mb-4">Deze vereenvoudigde calculator schat de optimale batterijgrootte op basis van uw jaarlijkse verbruikspatroon en het verschil tussen productie en direct verbruik (netimport).</p>
        """,
    }
    show_technical_details: bool = False

    @rx.event
    def toggle_technical_details(self):
        self.show_technical_details = not self.show_technical_details

    @rx.event
    async def load_page_content(self):
        from app.services.directus_service import DirectusService
        from app.utils.html_utils import clean_cms_html

        try:
            directus = DirectusService()
            module_data = directus.get_advice_module("simple-battery")
            if module_data:
                self.intro_content = {
                    "title": str(
                        module_data.get("intro_title") or self.intro_content["title"]
                    ),
                    "subtitle": str(
                        module_data.get("intro_subtitle")
                        or self.intro_content["subtitle"]
                    ),
                    "instructions": clean_cms_html(
                        module_data.get("intro_content")
                        or self.intro_content["instructions"]
                    ),
                }
                self.technical_details_content = {
                    "title": str(
                        module_data.get("technical_title")
                        or self.technical_details_content["title"]
                    ),
                    "content": clean_cms_html(
                        module_data.get("technical_content")
                        or self.technical_details_content["content"]
                    ),
                }
                return
        except Exception as e:
            logging.exception(
                f"Error loading simple-battery content from Directus: {e}"
            )

    @rx.event
    def close_email_modal(self):
        self.email_sent_modal_open = False

    @rx.var
    def annual_export(self) -> float:
        return max(0.0, self.annual_consumption - self.annual_grid_import)

    @rx.event
    def set_annual_consumption(self, value: str):
        if value:
            try:
                self.annual_consumption = float(value)
            except ValueError as e:
                logging.exception(f"Error setting annual consumption: {e}")

    @rx.event
    def set_annual_grid_import(self, value: str):
        if value:
            try:
                self.annual_grid_import = float(value)
            except ValueError as e:
                logging.exception(f"Error setting annual grid import: {e}")

    @rx.event
    def toggle_advanced_params(self):
        self.show_advanced_params = not self.show_advanced_params

    @rx.event
    def set_eta(self, value: str):
        if value:
            try:
                self.eta = float(value)
            except ValueError as e:
                logging.exception(f"Error setting eta: {e}")

    @rx.event
    def set_dod(self, value: str):
        if value:
            try:
                self.dod = float(value)
            except ValueError as e:
                logging.exception(f"Error setting dod: {e}")

    @rx.event
    def set_safety_factor(self, value: str):
        if value:
            try:
                self.safety_factor = float(value)
            except ValueError as e:
                logging.exception(f"Error setting safety_factor: {e}")

    @rx.event
    def set_electricity_price(self, value: str):
        if value:
            try:
                self.electricity_price = float(value)
            except ValueError as e:
                logging.exception(f"Error setting electricity_price: {e}")

    @rx.event
    def set_battery_cost_per_kwh(self, value: str):
        if value:
            try:
                self.battery_cost_per_kwh = float(value)
            except ValueError as e:
                logging.exception(f"Error setting battery_cost_per_kwh: {e}")

    @rx.var
    def rate_limit_status(self) -> str:
        return self.get_usage_status("simple_battery")

    @rx.event
    async def calculate_optimal_battery(self):
        if not self.check_can_execute("simple_battery"):
            msg = (
                "Dagelijkse limiet bereikt. Probeer het morgen opnieuw."
                if self.is_authenticated
                else "Dagelijkse limiet bereikt (5/5). Log in voor meer berekeningen."
            )
            yield rx.toast.error(msg)
            return
        self.is_processing = True
        self.has_calculated = False
        try:
            self.increment_usage("simple_battery")
            self.avg_daily_export = self.annual_export / 365.0
            self.usable_capacity = self.avg_daily_export * self.safety_factor
            calculated_nominal = self.usable_capacity / self.dod
            self.optimal_capacity = round(calculated_nominal * 2) / 2
            self.extra_self_consumption = self.annual_export * self.eta
            if self.annual_consumption > 0:
                self.percent_offset = (
                    self.extra_self_consumption / self.annual_consumption * 100.0
                )
            else:
                self.percent_offset = 0.0
            self.annual_savings = self.extra_self_consumption * self.electricity_price
            self.total_battery_cost = self.optimal_capacity * self.battery_cost_per_kwh
            if self.annual_savings > 0:
                self.payback_period = self.total_battery_cost / self.annual_savings
            else:
                self.payback_period = 99.9
            if self.total_battery_cost > 0:
                self.roi = self.annual_savings / self.total_battery_cost * 100.0
            else:
                self.roi = 0.0
            self.avg_daily_export = round(self.avg_daily_export, 2)
            self.usable_capacity = round(self.usable_capacity, 2)
            self.extra_self_consumption = round(self.extra_self_consumption, 1)
            self.percent_offset = round(self.percent_offset, 1)
            self.annual_savings = round(self.annual_savings, 2)
            self.payback_period = round(self.payback_period, 1)
            self.roi = round(self.roi, 1)
            self.has_calculated = True
            StatisticsService.track_calculation(
                self,
                "simple_battery",
                {
                    "annual_consumption": self.annual_consumption,
                    "annual_grid_import": self.annual_grid_import,
                    "battery_cost_per_kwh": self.battery_cost_per_kwh,
                    "electricity_price": self.electricity_price,
                    "eta": self.eta,
                    "dod": self.dod,
                },
                {
                    "annual_savings": self.annual_savings,
                    "payback_period": self.payback_period,
                    "percent_offset": self.percent_offset,
                    "optimal_capacity": self.optimal_capacity,
                },
            )
        except Exception as e:
            logging.exception(f"Simple battery calculation error: {e}")
        finally:
            self.is_processing = False

    @rx.event
    async def email_results(self):
        if not self.is_authenticated or not self.user:
            yield rx.toast.error("U moet ingelogd zijn om resultaten te mailen.")
            return
        self.is_sending_email = True
        yield
        try:
            user_email = self.user.get("email")
            subject = f"Uw Batterij Advies - {datetime.date.today()}"
            email_data = {
                "title": "Batterij Advies Rapport",
                "main_metric_label": "Aanbevolen Capaciteit",
                "main_metric_value": f"{self.optimal_capacity} kWh",
                "main_metric_sub": "Nominale Batterij Capaciteit",
                "stats": [
                    {
                        "label": "Bruikbare Capaciteit",
                        "value": f"{self.usable_capacity} kWh",
                    },
                    {
                        "label": "Jaarlijkse Besparing",
                        "value": f"€{self.annual_savings}",
                    },
                    {
                        "label": "Terugverdientijd",
                        "value": f"{self.payback_period} jaar",
                    },
                    {"label": "ROI", "value": f"{self.roi}%"},
                ],
                "details": [
                    ("Jaarlijks Verbruik", f"{self.annual_consumption} kWh"),
                    ("Net Import", f"{self.annual_grid_import} kWh"),
                    ("Extra Zelfconsumptie", f"+{self.extra_self_consumption} kWh"),
                    ("Compensatie Percentage", f"{self.percent_offset}%"),
                    ("Geschatte Kosten", f"€{self.total_battery_cost:.2f}"),
                ],
            }
            if EmailService.send_results_email(user_email, subject, email_data):
                self.email_sent_modal_open = True
            else:
                rx.toast.error("Kon e-mail niet verzenden. Probeer het later opnieuw.")
        except Exception as e:
            logging.exception(f"Error sending simple battery email: {e}")
            rx.toast.error("Er is een fout opgetreden bij het verzenden van de e-mail.")
        finally:
            self.is_sending_email = False