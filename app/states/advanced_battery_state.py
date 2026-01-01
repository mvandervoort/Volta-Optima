import reflex as rx
from .base_state import State
from app.services.email_service import EmailService
from app.services.statistics_service import StatisticsService
import datetime
import logging
import asyncio


class AdvancedBatteryState(State):
    is_processing: bool = False
    capacity: float = 10.0
    power: float = 5.0
    has_calculated: bool = False
    is_sending_email: bool = False
    email_sent_modal_open: bool = False
    intro_content: dict[str, str] = {
        "title": "Geavanceerde Batterij Simulatie",
        "subtitle": "Professionele simulatie met uw eigen uurlijkse verbruiksdata.",
        "instructions": """
<p>De Geavanceerde Batterij Simulatie is onze meest nauwkeurige tool voor het analyseren van batterijopslag. Door uw <strong>eigen uurlijkse meetgegevens</strong> te uploaden krijgt u een simulatie die exact is afgestemd op uw verbruikspatroon.</p>
""",
    }
    technical_details_content: dict[str, str] = {
        "title": "Technische Achtergrond & Simulatiemethode",
        "content": """
<h3 class="text-lg font-semibold text-gray-800 mb-2">Data Verwerking</h3>
<p class="mb-4">Uw geüploade CSV-bestand wordt gevalideerd en genormaliseerd naar een standaard formaat met 8.760 uurwaarden (365 dagen × 24 uur). Ontbrekende waarden worden geïnterpoleerd.</p>
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
            module_data = directus.get_advice_module("advanced-battery")
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
        except Exception as e:
            logging.exception(f"Error loading advanced-battery content: {e}")

    @rx.event
    def close_email_modal(self):
        self.email_sent_modal_open = False

    @rx.event
    def set_capacity(self, value: str):
        if value:
            self.capacity = float(value)

    @rx.event
    def set_power(self, value: str):
        if value:
            self.power = float(value)

    @rx.event
    async def start_simulation(self):
        self.is_processing = True
        self.has_calculated = False
        yield
        await asyncio.sleep(2)
        self.is_processing = False
        self.has_calculated = True
        StatisticsService.track_calculation(
            self,
            "advanced_battery",
            {"capacity": self.capacity, "power": self.power},
            {"status": "demo_complete", "message": "Simulation successful (demo mode)"},
        )
        yield rx.toast.success("Simulatie gestart (Demo Modus)")

    @rx.event
    async def email_results(self):
        if not self.is_authenticated or not self.user:
            yield rx.toast.error("U moet ingelogd zijn om resultaten te mailen.")
            return
        self.is_sending_email = True
        yield
        try:
            user_email = self.user.get("email")
            subject = f"Advanced Battery Simulation Report - {datetime.date.today()}"
            email_data = {
                "title": "Advanced Battery Simulation",
                "main_metric_label": "System Configuration",
                "main_metric_value": f"{self.capacity} kWh",
                "main_metric_sub": f"Inverter Power: {self.power} kW",
                "stats": [
                    {"label": "Simulation Status", "value": "Complete"},
                    {"label": "Data Source", "value": "Uploaded Profiles"},
                    {"label": "Optimization Type", "value": "Dynamic Pricing"},
                    {"label": "Report Type", "value": "Demo Simulation"},
                ],
                "details": [
                    ("Battery Capacity", f"{self.capacity} kWh"),
                    ("Inverter Power", f"{self.power} kW"),
                    ("Simulation Date", str(datetime.date.today())),
                    (
                        "Note",
                        "This is a demonstration report generated from the Advanced Battery Calculator.",
                    ),
                ],
            }
            if EmailService.send_results_email(user_email, subject, email_data):
                self.email_sent_modal_open = True
            else:
                rx.toast.error("Kon e-mail niet verzenden. Probeer het later opnieuw.")
        except Exception as e:
            logging.exception(f"Error sending advanced battery email: {e}")
            rx.toast.error("Er is een fout opgetreden bij het verzenden van de e-mail.")
        finally:
            self.is_sending_email = False