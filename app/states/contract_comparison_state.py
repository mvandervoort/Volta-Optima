import reflex as rx
from .base_state import State
import logging
import pandas as pd
import io
from app.services.questdb_client import QuestDBClient
from app.services.statistics_service import StatisticsService


class ContractComparisonState(State):
    consumption_profile: list[float] = []
    production_profile: list[float] = []
    consumption_status: str = "Geen bestand geüpload"
    production_status: str = "Geen bestand geüpload"
    fixed_purchase_price: float = 0.4
    fixed_feedin_price: float = 0.08
    variable_purchase_price: float = 0.35
    variable_feedin_price: float = 0.07
    is_calculating: bool = False
    has_results: bool = False
    error_message: str = ""
    fixed_results: dict[str, float] = {}
    variable_results: dict[str, float] = {}
    dynamic_results: dict[str, float] = {}
    comparison_chart_data: list[dict] = []
    intro_content: dict[str, str] = {
        "title": "Vergelijk Kosten Soort Contracten",
        "subtitle": "Vast, Variabel of Dynamisch? Ontdek welk energiecontract bij u past.",
        "instructions": """
<p>De keuze voor een energiecontract is belangrijker dan ooit. Met de opkomst van dynamische tarieven en de afbouw van de salderingsregeling is er geen 'one-size-fits-all' oplossing meer.</p>
<p class='mt-4'>Deze module helpt u binnenkort bij het vergelijken van:</p>
<ul class='list-disc pl-5 space-y-1 mt-2'>
    <li><strong>Vaste contracten:</strong> Zekerheid voor 1 of 3 jaar.</li>
    <li><strong>Variabele contracten:</strong> Flexibiliteit met prijswijzigingen per half jaar of kwartaal.</li>
    <li><strong>Dynamische contracten:</strong> Directe toegang tot beursprijzen (EPEX), ideaal voor slimme sturing.</li>
</ul>
""",
    }
    technical_details_content: dict[str, str] = {
        "title": "Berekeningsmethodiek & Bronnen",
        "content": """
<h3 class='text-lg font-semibold text-gray-800 mb-2'>Datagedreven Vergelijking</h3>
<p class='mb-4'>Onze vergelijkingstool gebruikt historische prijsdata en actuele markttrends om een realistische inschatting te maken van uw jaarlijkse kosten bij verschillende contractvormen.</p>
""",
    }
    show_technical_details: bool = False

    @rx.var
    def is_fixed_cheapest(self) -> bool:
        if not self.has_results:
            return False
        f = self.fixed_results.get("total_cost", float("inf"))
        v = self.variable_results.get("total_cost", float("inf"))
        d = self.dynamic_results.get("total_cost", float("inf"))
        return f <= v and f <= d

    @rx.var
    def is_variable_cheapest(self) -> bool:
        if not self.has_results:
            return False
        f = self.fixed_results.get("total_cost", float("inf"))
        v = self.variable_results.get("total_cost", float("inf"))
        d = self.dynamic_results.get("total_cost", float("inf"))
        return v < f and v <= d

    @rx.var
    def is_dynamic_cheapest(self) -> bool:
        if not self.has_results:
            return False
        f = self.fixed_results.get("total_cost", float("inf"))
        v = self.variable_results.get("total_cost", float("inf"))
        d = self.dynamic_results.get("total_cost", float("inf"))
        return d < f and d < v

    @rx.event
    def set_fixed_purchase_price(self, val: str):
        if val:
            try:
                self.fixed_purchase_price = float(val)
            except ValueError as e:
                logging.exception(f"Error setting fixed_purchase_price: {e}")

    @rx.event
    def set_fixed_feedin_price(self, val: str):
        if val:
            try:
                self.fixed_feedin_price = float(val)
            except ValueError as e:
                logging.exception(f"Error setting fixed_feedin_price: {e}")

    @rx.event
    def set_variable_purchase_price(self, val: str):
        if val:
            try:
                self.variable_purchase_price = float(val)
            except ValueError as e:
                logging.exception(f"Error setting variable_purchase_price: {e}")

    @rx.event
    def set_variable_feedin_price(self, val: str):
        if val:
            try:
                self.variable_feedin_price = float(val)
            except ValueError as e:
                logging.exception(f"Error setting variable_feedin_price: {e}")

    @rx.event
    def toggle_technical_details(self):
        self.show_technical_details = not self.show_technical_details

    @rx.event
    async def load_page_content(self):
        from app.services.directus_service import DirectusService
        from app.utils.html_utils import clean_cms_html

        try:
            directus = DirectusService()
            module_data = directus.get_advice_module("contract-vergelijking")
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
            logging.exception(f"Error loading contract-comparison content: {e}")

    async def _process_csv(self, file: rx.UploadFile, col_name: str) -> list[float]:
        """
        Reads a CSV file, looks for a specific column, and ensures 8760 hourly values.
        Normalizes 8784 (leap year) rows to 8760 by removing leap day (Feb 29) approximation.
        """
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        if col_name not in df.columns:
            df.columns = df.columns.str.strip()
            if col_name.strip() in df.columns:
                col_name = col_name.strip()
            else:
                raise ValueError(f"Kolom '{col_name}' niet gevonden in CSV.")
        data = df[col_name].fillna(0).tolist()
        if len(data) == 8784:
            data = data[:8760]
        elif len(data) == 8760:
            pass
        else:
            if len(data) < 8760:
                raise ValueError(
                    f"Te weinig data rijen: {len(data)}. Minimaal 8760 (1 jaar) vereist."
                )
            data = data[:8760]
        return [float(x) for x in data]

    @rx.event
    async def handle_consumption_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        try:
            file = files[0]
            self.consumption_profile = await self._process_csv(file, " Sum [kWh]")
            self.consumption_status = (
                f"✅ {file.name} ({len(self.consumption_profile)} uren)"
            )
            yield rx.toast.success("Verbruiksprofiel succesvol geladen")
        except Exception as e:
            logging.exception(f"Consumption upload error: {e}")
            self.consumption_status = "❌ Fout bij laden"
            yield rx.toast.error(f"Fout bij laden verbruik: {str(e)}")

    @rx.event
    async def handle_production_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        try:
            file = files[0]
            self.production_profile = await self._process_csv(file, "Yield")
            self.production_status = (
                f"✅ {file.name} ({len(self.production_profile)} uren)"
            )
            yield rx.toast.success("Productieprofiel succesvol geladen")
        except Exception as e:
            logging.exception(f"Production upload error: {e}")
            self.production_status = "❌ Fout bij laden"
            yield rx.toast.error(f"Fout bij laden productie: {str(e)}")

    @rx.event(background=True)
    async def calculate_comparison(self):
        async with self:
            if not self.consumption_profile or not self.production_profile:
                yield rx.toast.warning(
                    "Upload eerst beide profielen (Verbruik en Productie)."
                )
                return
            self.is_calculating = True
            self.error_message = ""
            self.has_results = False
        try:
            client = QuestDBClient()
            prices_data = client.get_dynamic_pricing(
                limit=10000, start_date="2024-01-01", end_date="2024-12-31"
            )
            if not prices_data:
                raise ValueError("Geen prijsdata beschikbaar uit database.")
            dynamic_prices = [p.get("Eindprijs", 0.0) for p in prices_data]
            if len(dynamic_prices) > 8760:
                dynamic_prices = dynamic_prices[:8760]
            elif len(dynamic_prices) < 8760:
                last_price = dynamic_prices[-1] if dynamic_prices else 0.35
                dynamic_prices.extend([last_price] * (8760 - len(dynamic_prices)))
            hours = min(
                len(self.consumption_profile),
                len(self.production_profile),
                len(dynamic_prices),
            )
            total_cons = 0.0
            total_prod = 0.0
            fixed_cost = 0.0
            variable_cost = 0.0
            dynamic_cost = 0.0
            month_names = [
                "Jan",
                "Feb",
                "Mrt",
                "Apr",
                "Mei",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Okt",
                "Nov",
                "Dec",
            ]
            monthly_data = [
                {"name": name, "Vast": 0.0, "Variabel": 0.0, "Dynamisch": 0.0}
                for name in month_names
            ]
            for i in range(hours):
                cons = self.consumption_profile[i]
                prod = self.production_profile[i]
                netto = cons - prod
                dyn_p_in = dynamic_prices[i]
                dyn_p_out = dyn_p_in * 0.7 if dyn_p_in > 0 else 0
                h_fixed = (
                    netto * self.fixed_purchase_price
                    if netto > 0
                    else netto * self.fixed_feedin_price
                )
                h_variable = (
                    netto * self.variable_purchase_price
                    if netto > 0
                    else netto * self.variable_feedin_price
                )
                h_dynamic = netto * dyn_p_in if netto > 0 else netto * dyn_p_out
                fixed_cost += h_fixed
                variable_cost += h_variable
                dynamic_cost += h_dynamic
                total_cons += cons
                total_prod += prod
                month_idx = min(int(i / 730), 11)
                monthly_data[month_idx]["Vast"] += h_fixed
                monthly_data[month_idx]["Variabel"] += h_variable
                monthly_data[month_idx]["Dynamisch"] += h_dynamic
            global_max = 1.0
            for m in monthly_data:
                global_max = max(global_max, m["Vast"], m["Variabel"], m["Dynamisch"])
            final_chart_data = []
            for m in monthly_data:
                final_chart_data.append(
                    {
                        "name": m["name"],
                        "Vast": round(m["Vast"], 2),
                        "Variabel": round(m["Variabel"], 2),
                        "Dynamisch": round(m["Dynamisch"], 2),
                        "Vast_pct": int(m["Vast"] / global_max * 100),
                        "Variabel_pct": int(m["Variabel"] / global_max * 100),
                        "Dynamisch_pct": int(m["Dynamisch"] / global_max * 100),
                    }
                )
            async with self:
                self.fixed_results = {
                    "total_cost": round(fixed_cost, 2),
                    "avg_monthly": round(fixed_cost / 12, 2),
                }
                self.variable_results = {
                    "total_cost": round(variable_cost, 2),
                    "avg_monthly": round(variable_cost / 12, 2),
                }
                self.dynamic_results = {
                    "total_cost": round(dynamic_cost, 2),
                    "avg_monthly": round(dynamic_cost / 12, 2),
                }
                self.comparison_chart_data = final_chart_data
                self.has_results = True
                StatisticsService.track_calculation(
                    self,
                    "contract_comparison",
                    {
                        "total_consumption": round(total_cons, 2),
                        "total_production": round(total_prod, 2),
                        "contract_prices": {
                            "fixed": [
                                self.fixed_purchase_price,
                                self.fixed_feedin_price,
                            ],
                            "variable": [
                                self.variable_purchase_price,
                                self.variable_feedin_price,
                            ],
                        },
                    },
                    {
                        "fixed_total": round(fixed_cost, 2),
                        "variable_total": round(variable_cost, 2),
                        "dynamic_total": round(dynamic_cost, 2),
                    },
                )
        except Exception as e:
            logging.exception(f"Contract calculation error: {e}")
            async with self:
                self.error_message = f"Er is een fout opgetreden: {str(e)}"
        finally:
            async with self:
                self.is_calculating = False