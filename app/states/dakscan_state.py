import reflex as rx
import os
import requests
import logging
import datetime
from app.services.questdb_client import QuestDBClient
from app.services.email_service import EmailService
from app.services.statistics_service import StatisticsService
from .base_state import State


class DakscanState(State):
    address: str = ""
    result_data: dict = {}
    is_loading: bool = False
    error_message: str = ""
    has_results: bool = False
    panels_count: int = 0
    roof_area: float = 0.0
    annual_yield: float = 0.0
    annual_savings: float = 0.0
    co2_offset: float = 0.0
    sunshine_hours: float = 0.0
    max_arrays: int = 0
    roof_segments: list[dict] = []
    is_sending_email: bool = False
    email_sent_modal_open: bool = False
    intro_content: dict[str, str] = {
        "title": "Dakscan: Zonnepotentieel Analyse",
        "subtitle": "Ontdek hoeveel zonne-energie uw dak kan opwekken met Google Solar AI technologie.",
        "instructions": """
        <p>Met de Dakscan analyseert u in enkele seconden het zonnepotentieel van uw woning. Deze tool maakt gebruik van de geavanceerde <strong>Google Solar API</strong> die satellietbeelden en machine learning combineert om een nauwkeurige inschatting te maken van uw dak.</p>
        <p class="mt-4"><strong>Wat de Dakscan voor u doet:</strong></p>
        <ul class="list-disc pl-5 space-y-1 mt-2">
            <li>Analyseert automatisch uw dakoppervlak, oriëntatie en hellingshoek</li>
            <li>Berekent het maximale aantal zonnepanelen dat past op uw dak</li>
            <li>Schat de jaarlijkse energieopbrengst in kWh</li>
            <li>Toont potentiële CO₂-besparing en financieel voordeel</li>
        </ul>
        """,
    }
    technical_details_content: dict[str, str] = {
        "title": "Technische Achtergrond & Methodiek",
        "content": """
        <h3 class="text-lg font-semibold text-gray-800 mb-2">Google Solar API Technologie</h3>
        <p class="mb-4">De Dakscan maakt gebruik van de <strong>Google Solar API (Building Insights)</strong>, een geavanceerde service die high-resolution satellietbeelden combineert met machine learning modellen om dakkenmerken te analyseren.</p>
        <h3 class="text-lg font-semibold text-gray-800 mb-2">Analysemethode</h3>
        <ul class="list-disc pl-5 space-y-2 text-gray-600 mb-4">
            <li><strong>3D Dakmodel:</strong> Google's algoritme reconstrueert een 3D-model van uw dak op basis van luchtfoto's en LiDAR-data waar beschikbaar.</li>
            <li><strong>Schaduwanalyse:</strong> Er wordt rekening gehouden met schaduw van omliggende gebouwen, bomen en andere obstakels gedurende het hele jaar.</li>
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
            module_data = directus.get_advice_module("dakscan")
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
            logging.exception(f"Error loading dakscan content from Directus: {e}")

    def _get_compass_direction(self, degrees: float) -> str:
        """Convert azimuth degrees (0=N, 90=E) to Dutch compass abbreviation."""
        dirs = ["N", "NO", "O", "ZO", "Z", "ZW", "W", "NW"]
        idx = round(degrees % 360 / 45) % 8
        return dirs[idx]

    @rx.event
    def set_address(self, value: str):
        self.address = value

    @rx.event
    def close_email_modal(self):
        self.email_sent_modal_open = False

    @rx.event
    def set_address(self, value: str):
        self.address = value

    @rx.event(background=True)
    async def analyze_roof(self):
        async with self:
            if not self.address:
                self.error_message = "Voer a.u.b. een geldig adres in."
                return
            self.is_loading = True
            self.error_message = ""
            self.has_results = False
            self.result_data = {}
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            async with self:
                self.error_message = (
                    "System configuration error: Google API Key missing."
                )
                self.is_loading = False
                return
        lat, lon = (0.0, 0.0)
        try:
            geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {"address": self.address, "key": api_key}
            resp = requests.get(geocode_url, params=params, timeout=10)
            data = resp.json()
            if data.get("status") == "OK":
                loc = data["results"][0]["geometry"]["location"]
                lat, lon = (loc["lat"], loc["lng"])
                formatted_addr = data["results"][0].get(
                    "formatted_address", self.address
                )
            else:
                async with self:
                    self.error_message = f"Adres niet gevonden. ({data.get('status')})"
                    self.is_loading = False
                return
        except Exception as e:
            logging.exception(f"Geocoding error: {e}")
            async with self:
                self.error_message = (
                    "Kon locatie niet bepalen. Controleer uw verbinding."
                )
                self.is_loading = False
            return
        solar_data = None
        try:
            solar_url = "https://solar.googleapis.com/v1/buildingInsights:findClosest"
            params = {
                "location.latitude": lat,
                "location.longitude": lon,
                "requiredQuality": "HIGH",
                "key": api_key,
            }
            logging.info(
                f"Requesting Solar API (HIGH quality) for lat={lat}, lon={lon}"
            )
            resp = requests.get(solar_url, params=params, timeout=15)
            should_retry = False
            if resp.status_code == 404:
                should_retry = True
            elif resp.status_code != 200:
                try:
                    err_body = resp.json()
                    err_msg = err_body.get("error", {}).get("message", "").lower()
                    if "not found" in err_msg or "entity" in err_msg:
                        should_retry = True
                except ValueError as e:
                    logging.exception(f"Error parsing error response: {e}")
                    pass
            if should_retry:
                logging.info(
                    "HIGH quality request failed or not found. Retrying with MEDIUM quality."
                )
                params["requiredQuality"] = "MEDIUM"
                resp = requests.get(solar_url, params=params, timeout=15)
            if resp.status_code == 200:
                solar_data = resp.json()
                logging.info("Solar API request successful.")
            else:
                try:
                    err_body = resp.json()
                    err_msg = err_body.get("error", {}).get(
                        "message", "Onbekende fout bij Solar API"
                    )
                except ValueError as e:
                    logging.exception(f"Error parsing error response: {e}")
                    err_body = resp.text
                    err_msg = f"HTTP {resp.status_code}"
                logging.error(
                    f"Solar API Error (Status {resp.status_code}): {err_body}"
                )
                async with self:
                    if (
                        "out of coverage" in err_msg.lower()
                        or "not found" in err_msg.lower()
                    ):
                        self.error_message = (
                            "Helaas, geen zonnedata beschikbaar voor deze locatie."
                        )
                    else:
                        self.error_message = f"Solar API fout: {err_msg}"
                    self.is_loading = False
                return
        except Exception as e:
            logging.exception(f"Solar API connection error: {e}")
            async with self:
                self.error_message = "Kon geen verbinding maken met de Solar service."
                self.is_loading = False
            return
        if solar_data:
            sp = solar_data.get("solarPotential", {})
            max_panels = sp.get("maxArrayPanelsCount", 0)
            max_area = sp.get("maxArrayAreaMeters2", 0.0)
            max_sunshine = sp.get("maxSunshineHoursPerYear", 0.0)
            configs = sp.get("solarPanelConfigs", [])
            yearly_energy_kwh = 0.0
            if configs:
                best_config = max(configs, key=lambda x: x.get("panelsCount", 0))
                yearly_energy_kwh = best_config.get("yearlyEnergyDcKwh", 0.0)
            if yearly_energy_kwh == 0 and max_panels > 0:
                yearly_energy_kwh = max_panels * 320
            segments = []
            for i, seg in enumerate(sp.get("roofSegmentStats", [])):
                stats = seg.get("stats", {})
                area = stats.get("areaMeters2", 0.0)
                azimuth = seg.get("azimuthDegrees", 0.0)
                pitch = seg.get("pitchDegrees", 0.0)
                if area >= 1.0:
                    segments.append(
                        {
                            "area": round(area, 1),
                            "azimuth": round(azimuth, 0),
                            "pitch": round(pitch, 0),
                            "direction": self._get_compass_direction(azimuth),
                        }
                    )
            segments.sort(key=lambda x: x["area"], reverse=True)
            for idx, seg in enumerate(segments):
                seg["index"] = idx + 1
            client = QuestDBClient()
            stats = client.get_price_statistics(period="year")
            avg_price = stats.get("avg_price", 0.35)
            est_savings = yearly_energy_kwh * avg_price
            co2 = yearly_energy_kwh * 0.35
            async with self:
                self.result_data = solar_data
                self.panels_count = int(max_panels)
                self.roof_area = round(max_area, 1)
                self.sunshine_hours = round(max_sunshine, 0)
                self.annual_yield = round(yearly_energy_kwh, 0)
                self.annual_savings = round(est_savings, 0)
                self.co2_offset = round(co2, 0)
                self.max_arrays = len(sp.get("roofSegmentStats", []))
                self.roof_segments = segments
                self.has_results = True
                self.is_loading = False
            StatisticsService.track_calculation(
                self,
                "dakscan",
                {"address": self.address, "lat": lat, "lon": lon},
                {
                    "yield_kwh": yearly_energy_kwh,
                    "savings_eur": est_savings,
                    "panels": max_panels,
                },
            )
        else:
            async with self:
                self.error_message = "Geen bruikbare data ontvangen."
                self.is_loading = False

    @rx.event
    async def email_results(self):
        if not self.is_authenticated or not self.user:
            yield rx.toast.error("U moet ingelogd zijn om resultaten te mailen.")
            return
        self.is_sending_email = True
        yield
        try:
            user_email = self.user.get("email")
            subject = f"Uw Dakscan Resultaten - {datetime.date.today()}"
            email_data = {
                "title": "Dakscan Rapport",
                "main_metric_label": "Geschatte Jaaropbrengst",
                "main_metric_value": f"{self.annual_yield} kWh",
                "main_metric_sub": f"Potentieel voor {self.panels_count} panelen",
                "stats": [
                    {
                        "label": "Jaarlijkse Besparing",
                        "value": f"€{self.annual_savings}",
                    },
                    {"label": "Dak Beschikbaar", "value": f"{self.roof_area} m²"},
                    {"label": "Zonuren", "value": f"{self.sunshine_hours} uur/jr"},
                    {"label": "CO₂ Compensatie", "value": f"{self.co2_offset} kg"},
                ],
                "details": [
                    ("Adres", self.address),
                    ("Aantal Daksegmenten", str(self.max_arrays)),
                    ("Datum", str(datetime.date.today())),
                ],
            }
            if EmailService.send_results_email(user_email, subject, email_data):
                self.email_sent_modal_open = True
            else:
                rx.toast.error("Kon e-mail niet verzenden.")
        except Exception as e:
            logging.exception(f"Error sending dakscan email: {e}")
            rx.toast.error("Er is een fout opgetreden bij het verzenden van de e-mail.")
        finally:
            self.is_sending_email = False