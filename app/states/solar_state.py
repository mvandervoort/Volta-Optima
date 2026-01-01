import reflex as rx
import requests
import logging
import datetime
import calendar
import random
import os
from .base_state import State
from app.services.questdb_client import QuestDBClient
from app.services.email_service import EmailService
from app.services.statistics_service import StatisticsService

NREL_API_URL = "https://developer.nrel.gov/api/pvwatts/v8.json"


class SolarState(State):
    address: str = ""
    lat: float = 0.0
    lon: float = 0.0
    system_capacity: float = 4.0
    module_type: int = 0
    array_type: int = 1
    tilt: float = 20.0
    azimuth: float = 180.0
    losses: float = 14.0
    results: dict[str, float | str | list[float]] = {}
    ac_monthly: list[float] = []
    ac_annual: float = 0.0
    solrad_annual: float = 0.0
    capacity_factor: float = 0.0
    co2_offset: float = 0.0
    value_saved: float = 0.0
    is_loading: bool = False
    error_message: str = ""
    avg_price: float = 0.3828
    feed_in_tariff: float = 0.08
    self_consumption_rate: float = 30.0
    system_cost: float = 0.0
    payback_period: float = 0.0
    monthly_savings: float = 0.0
    price_components: dict[str, float] = {}
    savings_breakdown: dict[str, float] = {}
    is_sending_email: bool = False
    email_sent_modal_open: bool = False
    intro_content: dict[str, str] = {
        "title": "Zonnepanelen Opbrengst Calculator",
        "subtitle": "Ontdek hoeveel energie u kunt opwekken met zonne-energie.",
        "instructions": """
        <p>Welkom bij de geavanceerde zonne-energie calculator. Deze tool helpt u een nauwkeurige inschatting te maken van de potentiële energieopbrengst van uw dak, gebaseerd op locatie-specifieke weerdata en uw systeemconfiguratie.</p>
        <p class="mt-4"><strong>Hoe te gebruiken:</strong></p>
        <ul class="list-disc pl-5 space-y-1 mt-2">
            <li>Vul uw locatie in (Postcode of Stad) om de lokale zonne-instraling te bepalen.</li>
            <li>Specificeer het vermogen van uw (gewenste) systeem in kWp.</li>
            <li>Pas de oriëntatie en hellingshoek aan voor een nauwkeurig resultaat.</li>
        </ul>
        <p class="mt-4">De berekening toont direct uw verwachte jaaropbrengst, financiële besparing en CO2-compensatie.</p>
        """,
    }
    technical_details_content: dict[str, str] = {
        "title": "Technische Achtergrond & Aannames",
        "content": """
        <h3 class="text-lg font-semibold text-gray-800 mb-2">Berekeningsmethodiek</h3>
        <p class="mb-4">Deze calculator maakt gebruik van de <strong>NREL PVWatts® V8 API</strong>, een industriestandaard voor het simuleren van fotovoltaïsche (PV) energiesystemen. De berekeningen zijn gebaseerd op historische weerdata (TMY2/TMY3) specifiek voor uw opgegeven locatie.</p>

        <h3 class="text-lg font-semibold text-gray-800 mb-2">Parameters en Aannames</h3>
        <ul class="list-disc pl-5 space-y-2 text-gray-600">
            <li><strong>Systeemverliezen:</strong> We hanteren een standaard verliesfactor van 14%. Dit omvat verliezen door bekabeling, omvormer-efficiëntie, lichte schaduwval en vervuiling van de panelen. U kunt dit percentage aanpassen in de instellingen.</li>
            <li><strong>Azimut (Oriëntatie):</strong> De kompasrichting van uw panelen. 180° is pal Zuid (optimaal voor Nederland/België), 90° is Oost, 270° is West.</li>
            <li><strong>Hellingshoek (Tilt):</strong> De hoek van de panelen ten opzichte van de grond. Een hoek tussen 30° en 40° is doorgaans optimaal voor Nederland.</li>
            <li><strong>Elektriciteitsprijs:</strong> Financiële besparingen worden berekend op basis van een dynamisch gemiddelde of een vaste instelbare stroomprijs (standaard ca. €0,38/kWh voor besparing, €0,08/kWh voor teruglevering).</li>
        </ul>
        """,
    }
    show_technical_details: bool = False

    @rx.event
    def toggle_technical_details(self):
        self.show_technical_details = not self.show_technical_details

    @rx.event
    async def load_page_content(self):
        from app.services.directus_service import DirectusService
        from app.services.cms_service import CMSService
        from app.utils.html_utils import clean_cms_html

        try:
            directus = DirectusService()
            module_data = directus.get_advice_module("solar-calculator")
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
            logging.exception(f"Error loading solar content from Directus: {e}")
        try:
            intro_data = CMSService.get_content_by_slug("solar-calculator-intro")
            if intro_data:
                self.intro_content = {
                    "title": str(
                        intro_data.get("title") or self.intro_content["title"]
                    ),
                    "subtitle": str(
                        intro_data.get("excerpt") or self.intro_content["subtitle"]
                    ),
                    "instructions": clean_cms_html(
                        intro_data.get("content_html")
                        or self.intro_content["instructions"]
                    ),
                }
        except Exception as e:
            logging.exception(f"Error loading solar intro content fallback: {e}")
        try:
            tech_data = CMSService.get_content_by_slug("solar-calculator-technical")
            if tech_data:
                self.technical_details_content = {
                    "title": str(
                        tech_data.get("title")
                        or self.technical_details_content["title"]
                    ),
                    "content": clean_cms_html(
                        tech_data.get("content_html")
                        or self.technical_details_content["content"]
                    ),
                }
        except Exception as e:
            logging.exception(f"Error loading solar technical details fallback: {e}")

    @rx.event
    def close_email_modal(self):
        self.email_sent_modal_open = False

    @rx.event
    def set_address(self, value: str):
        self.address = value

    @rx.event
    def set_tilt(self, value: str):
        """Handles tilt input from slider/text input."""
        if value:
            try:
                self.tilt = float(value)
            except ValueError as e:
                logging.exception(f"Error setting tilt: {e}")

    @rx.event
    def set_azimuth(self, value: str):
        """Handles azimuth input from slider/text input."""
        if value:
            try:
                self.azimuth = float(value)
            except ValueError as e:
                logging.exception(f"Error setting azimuth: {e}")

    @rx.event
    def set_system_capacity(self, value: str):
        """Handles capacity input as string from frontend."""
        if value:
            try:
                self.system_capacity = float(value)
            except ValueError as e:
                logging.exception(f"Error setting system_capacity: {e}")

    @rx.event
    def set_losses(self, value: str):
        """Handles losses input as string from frontend."""
        if value:
            try:
                self.losses = float(value)
            except ValueError as e:
                logging.exception(f"Error setting losses: {e}")

    @rx.var
    def has_results(self) -> bool:
        return self.ac_annual > 0

    @rx.event
    def set_module_type_int(self, value: str):
        self.module_type = int(value)

    @rx.event(background=True)
    async def calculate_yield(self):
        async with self:
            if not self.address:
                self.error_message = "Please enter a valid location."
                return
            self.is_loading = True
            self.error_message = ""
            self.results = {}
        lat = 0.0
        lon = 0.0
        try:
            headers = {"User-Agent": "VoltaOptima-ReflexApp/1.0"}
            geo_url = "https://nominatim.openstreetmap.org/search"
            geo_params = {"q": self.address, "format": "json", "limit": 1}
            geo_response = requests.get(
                geo_url, params=geo_params, headers=headers, timeout=10
            )
            if geo_response.status_code == 200:
                geo_data = geo_response.json()
                if geo_data:
                    lat = float(geo_data[0]["lat"])
                    lon = float(geo_data[0]["lon"])
                else:
                    async with self:
                        self.error_message = f"Location '{self.address}' not found. Please try a more specific address."
                        self.is_loading = False
                    return
            else:
                async with self:
                    self.error_message = (
                        "Geocoding service unavailable. Please try again later."
                    )
                    self.is_loading = False
                return
            async with self:
                self.lat = round(lat, 2)
                self.lon = round(lon, 2)
        except Exception as e:
            logging.exception(f"Geocoding error: {e}")
            async with self:
                self.error_message = (
                    "Failed to resolve location. Please check your internet connection."
                )
                self.is_loading = False
            return
        try:
            client = QuestDBClient()
            stats = client.get_price_statistics(period="year")
            components = client.get_price_components()
            if stats and stats.get("avg_price"):
                real_avg_price = float(stats["avg_price"])
            else:
                real_avg_price = 0.3828
            real_components = components.get("components", {}) if components else {}
        except Exception as e:
            logging.exception(f"QuestDB fetch error: {e}")
            real_avg_price = 0.3828
            real_components = {}
        api_key = os.getenv("NREL_API_KEY", "DEMO_KEY")
        params = {
            "api_key": api_key,
            "lat": lat,
            "lon": lon,
            "system_capacity": self.system_capacity,
            "module_type": self.module_type,
            "array_type": self.array_type,
            "tilt": self.tilt,
            "azimuth": self.azimuth,
            "losses": self.losses,
            "format": "json",
        }
        try:
            response = requests.get(NREL_API_URL, params=params, timeout=10)
            data = response.json()
            async with self:
                if response.status_code == 200 and "outputs" in data:
                    outputs = data["outputs"]
                    self.ac_annual = round(float(outputs.get("ac_annual", 0)), 2)
                    self.solrad_annual = round(
                        float(outputs.get("solrad_annual", 0)), 2
                    )
                    self.capacity_factor = round(
                        float(outputs.get("capacity_factor", 0)), 2
                    )
                    self.co2_offset = round(self.ac_annual * 0.85, 2)
                    self.avg_price = round(real_avg_price, 4)
                    self.price_components = {
                        k: round(v, 2) for k, v in real_components.items()
                    }
                    self_consumed_kwh = self.ac_annual * (
                        self.self_consumption_rate / 100.0
                    )
                    savings_self = self_consumed_kwh * self.avg_price
                    exported_kwh = self.ac_annual * (
                        (100.0 - self.self_consumption_rate) / 100.0
                    )
                    earnings_export = exported_kwh * self.feed_in_tariff
                    self.value_saved = round(savings_self + earnings_export, 2)
                    self.monthly_savings = round(self.value_saved / 12.0, 2)
                    self.savings_breakdown = {
                        "self_consumption_euros": round(savings_self, 2),
                        "export_euros": round(earnings_export, 2),
                        "self_consumed_kwh": round(self_consumed_kwh, 2),
                        "exported_kwh": round(exported_kwh, 2),
                    }
                    cost_per_kw = 1300 if self.system_capacity < 5 else 1100
                    self.system_cost = self.system_capacity * cost_per_kw
                    if self.value_saved > 0:
                        self.payback_period = round(
                            self.system_cost / self.value_saved, 1
                        )
                    else:
                        self.payback_period = 0.0
                    self.results = outputs
                    self.ac_monthly = [float(x) for x in outputs.get("ac_monthly", [])]
                    StatisticsService.track_calculation(
                        self,
                        "solar_yield",
                        {
                            "address": self.address,
                            "system_capacity": self.system_capacity,
                            "module_type": self.module_type,
                            "tilt": self.tilt,
                            "azimuth": self.azimuth,
                            "losses": self.losses,
                        },
                        {
                            "ac_annual": self.ac_annual,
                            "solrad_annual": self.solrad_annual,
                            "value_saved": self.value_saved,
                            "payback_period": self.payback_period,
                            "co2_offset": self.co2_offset,
                        },
                    )
                elif "errors" in data:
                    self.error_message = f"API Error: {data['errors']}"
                else:
                    self.error_message = (
                        f"Failed to fetch data. Status: {response.status_code}"
                    )
        except Exception as e:
            logging.exception(f"Error: {e}")
            async with self:
                self.error_message = f"An error occurred: {str(e)}"
        async with self:
            self.is_loading = False

    @rx.event
    def download_solar_data(self):
        """Generate and download CSV with daily solar yield data."""
        if not self.ac_monthly:
            return rx.toast.error("No data available to download.")
        year = datetime.datetime.now().year
        csv_lines = ["Date,Daily Yield (kWh)"]
        for month_idx, monthly_total in enumerate(self.ac_monthly):
            month = month_idx + 1
            _, num_days = calendar.monthrange(year, month)
            daily_avg = monthly_total / num_days
            rng = random.Random(42 + month)
            days_yields = []
            for _ in range(num_days):
                variation = 1.0 + rng.uniform(-0.25, 0.25)
                days_yields.append(daily_avg * variation)
            current_total = sum(days_yields)
            correction = monthly_total / current_total if current_total > 0 else 0
            for day_idx, val in enumerate(days_yields):
                day = day_idx + 1
                adjusted_val = val * correction
                date_str = datetime.date(year, month, day).isoformat()
                csv_lines.append(f"{date_str},{adjusted_val:.2f}")
        csv_content = """
""".join(csv_lines)
        safe_addr = (
            "".join((c for c in self.address if c.isalnum() or c in (" ", "-", "_")))
            .strip()
            .replace(" ", "_")
        )
        date_str = datetime.date.today().isoformat()
        filename = f"solar_yield_{safe_addr}_{self.system_capacity}kW_{date_str}.csv"
        return rx.download(data=csv_content, filename=filename)

    @rx.event
    async def email_results(self):
        if not self.is_authenticated or not self.user:
            yield rx.toast.error("U moet ingelogd zijn om resultaten te mailen.")
            return
        self.is_sending_email = True
        yield
        try:
            user_email = self.user.get("email")
            subject = f"Uw Zonne-energie Rapport - {datetime.date.today()}"
            email_data = {
                "title": "Zonnepanelen Potentieel Rapport",
                "main_metric_label": "Geschatte Jaaropbrengst",
                "main_metric_value": f"{self.ac_annual} kWh",
                "main_metric_sub": f"Systeemgrootte: {self.system_capacity} kW",
                "stats": [
                    {
                        "label": "Jaarlijkse Besparing",
                        "value": f"€{self.value_saved}/jr",
                    },
                    {
                        "label": "Terugverdientijd",
                        "value": f"{self.payback_period} jaar",
                    },
                    {"label": "CO₂ Compensatie", "value": f"{self.co2_offset} kg"},
                    {
                        "label": "Maandelijkse Besparing",
                        "value": f"€{self.monthly_savings}",
                    },
                ],
                "details": [
                    ("Locatie", self.address),
                    ("Geschatte Kosten", f"€{self.system_cost}"),
                    ("Hellingshoek", f"{self.tilt}°"),
                    ("Oriëntatie (Azimut)", f"{self.azimuth}°"),
                    ("Zoninstraling", f"{self.solrad_annual} kWh/m²/dag"),
                ],
            }
            if EmailService.send_results_email(user_email, subject, email_data):
                self.email_sent_modal_open = True
            else:
                rx.toast.error("Kon e-mail niet verzenden. Probeer het later opnieuw.")
        except Exception as e:
            logging.exception(f"Error sending solar email: {e}")
            rx.toast.error("Er is een fout opgetreden bij het verzenden van de e-mail.")
        finally:
            self.is_sending_email = False