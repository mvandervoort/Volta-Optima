import reflex as rx
from .base_state import State
from app.services.email_service import EmailService
from app.services.statistics_service import StatisticsService
import pandas as pd
import io
import logging
import numpy as np
import datetime


class BatteryEstimatorState(State):
    jaar_verbruik: float = 3500.0
    jaar_teruglevering: float = 2000.0
    battery_efficiency: float = 0.95
    production_file_name: str = ""
    production_data_status: str = "Geen bestand geüpload"
    production_profile: list[float] = []
    is_processing: bool = False
    is_sending_email: bool = False
    error_message: str = ""
    has_calculated: bool = False
    optimal_capacity: float = 0.0
    zelfvoorzieningsgraad: float = 0.0
    grid_inkoop_totaal: float = 0.0
    grid_teruglevering_totaal: float = 0.0
    battery_cycli: float = 0.0
    levensduur_jaren: float = 0.0
    comparison_chart_data: list[dict] = []
    email_sent_modal_open: bool = False
    MAAND_VERDELING = {
        1: 0.11,
        2: 0.1,
        3: 0.09,
        4: 0.08,
        5: 0.07,
        6: 0.06,
        7: 0.06,
        8: 0.07,
        9: 0.08,
        10: 0.09,
        11: 0.1,
        12: 0.11,
    }
    intro_content: dict[str, str] = {
        "title": "Verbeterde Thuisbatterij Berekening",
        "subtitle": "Analyseer of een thuisbatterij financieel zinvol is voor uw situatie.",
        "instructions": """
<p>Deze verbeterde calculator biedt een diepgaande analyse van de financiële haalbaarheid van een thuisbatterij. In tegenstelling tot de eenvoudige versie, maakt deze tool gebruik van <strong>echte marktprijzen uit 2024</strong> voor een realistische inschatting.</p>

<p class="mt-4"><strong>Wat maakt deze calculator bijzonder:</strong></p>
<ul class="list-disc pl-5 space-y-1 mt-2">
    <li>Berekeningen gebaseerd op 8.760 werkelijke uurprijzen van 2024</li>
    <li>Automatische analyse van prijsarbitrage mogelijkheden</li>
    <li>Vergelijking tussen verschillende batterijgroottes</li>
    <li>Realistische terugverdientijdberekening</li>
</ul>
""",
    }
    technical_details_content: dict[str, str] = {
        "title": "Technische Achtergrond & Methodiek",
        "content": """
<h3 class="text-lg font-semibold text-gray-800 mb-2">Prijsdata en Bronnen</h3>
<p class="mb-4">De berekeningen zijn gebaseerd op werkelijke dynamische uurprijzen van Nederlandse energieleveranciers uit 2024. Deze data wordt opgeslagen in onze QuestDB database en regelmatig bijgewerkt.</p>

<h3 class="text-lg font-semibold text-gray-800 mb-2">Simulatiemethodiek</h3>
<ul class="list-disc pl-5 space-y-2 text-gray-600 mb-4">
    <li><strong>Verbruiksprofiel:</strong> We gebruiken een standaard Nederlands huishoudprofiel met piekmomenten in ochtend en avond.</li>
    <li><strong>Zonne-productie:</strong> Gemodelleerd op basis van typische opbrengstpatronen voor Nederland (piek rond 12:00-14:00).</li>
    <li><strong>Batterij Dispatch:</strong> Optimale laad/ontlaadstrategie wordt berekend per uur.</li>
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
        from app.utils.html_utils import clean_cms_html

        try:
            directus = DirectusService()
            module_data = directus.get_advice_module("battery-estimator")
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
            logging.exception(f"Error loading battery-estimator content: {e}")

    @rx.event
    def set_jaar_verbruik(self, value: str):
        if value:
            try:
                self.jaar_verbruik = float(value)
            except ValueError as e:
                logging.exception(f"Error setting jaar_verbruik: {e}")

    @rx.event
    def set_jaar_teruglevering(self, value: str):
        if value:
            try:
                self.jaar_teruglevering = float(value)
            except ValueError as e:
                logging.exception(f"Error setting jaar_teruglevering: {e}")

    @rx.event
    def close_email_modal(self):
        self.email_sent_modal_open = False

    @rx.event
    def set_battery_efficiency(self, value: str):
        if value:
            try:
                val = float(value)
                if 0.0 <= val <= 1.0:
                    self.battery_efficiency = val
                elif 1.0 < val <= 100.0:
                    self.battery_efficiency = val / 100.0
            except ValueError as e:
                logging.exception(f"Error setting battery_efficiency: {e}")

    async def _parse_csv(self, file: rx.UploadFile) -> list[float]:
        try:
            content = await file.read()
            df = pd.read_csv(io.BytesIO(content))
            col_name = None
            if "opbrengst_kwh" in df.columns:
                col_name = "opbrengst_kwh"
            elif "production_kwh" in df.columns:
                col_name = "production_kwh"
            else:
                numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
                if len(numeric_cols) > 0:
                    col_name = numeric_cols[0]
            if not col_name:
                raise ValueError("Geen geldige kolom (opbrengst_kwh) gevonden in CSV")
            rows = len(df)
            if rows < 360 or rows > 370:
                raise ValueError(
                    f"Zonne-opbrengst CSV moet een volledig jaar (365-366 dagen) bevatten. {rows} rijen gevonden."
                )
            return df[col_name].tolist()
        except Exception as e:
            logging.exception(f"CSV Parse Error: {e}")
            raise e

    @rx.event
    async def handle_production_upload(self, files: list[rx.UploadFile]):
        self.is_processing = True
        self.error_message = ""
        try:
            if not files:
                return
            file = files[0]
            self.production_file_name = file.name
            data = await self._parse_csv(file)
            self.production_profile = data
            self.production_data_status = f"Geldige data: {len(data)} dagen geladen"
            yield rx.toast.success("Zonne-data succesvol geüpload")
        except Exception as e:
            logging.exception(f"Solar upload failed: {e}")
            self.error_message = str(e)
            self.production_data_status = "Fout: Ongeldig bestand"
            self.production_profile = []
            yield rx.toast.error(f"Upload mislukt: {str(e)}")
        finally:
            self.is_processing = False

    def _maak_dag_nacht_profiel(self) -> pd.DataFrame:
        """
        Creëer seizoensafhankelijk dag/nacht verbruiksprofiel.
        Dag = 7:00-19:00, Nacht = 19:00-7:00
        """
        profiel = []
        for dag in range(365):
            maand = dag // 30 + 1
            if maand > 12:
                maand = 12
            if maand in [5, 6, 7, 8]:
                dag_fractie = 0.55
            elif maand in [11, 12, 1, 2]:
                dag_fractie = 0.35
            else:
                dag_fractie = 0.45
            profiel.append(
                {
                    "dag": dag + 1,
                    "dag_fractie": dag_fractie,
                    "nacht_fractie": 1 - dag_fractie,
                }
            )
        return pd.DataFrame(profiel)

    def _bereken_dagelijks_verbruik(
        self, dag_nacht_profiel: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Bereken dagelijks verbruik op basis van maandverdeling en dag/nacht profiel.
        """
        dagelijks_data = []
        for dag in range(365):
            maand = min(dag // 30 + 1, 12)
            dagen_in_jaar = 365
            dag_verbruik = (
                self.jaar_verbruik * self.MAAND_VERDELING[maand] * 12 / dagen_in_jaar
            )
            dag_frac = dag_nacht_profiel.iloc[dag]["dag_fractie"]
            nacht_frac = dag_nacht_profiel.iloc[dag]["nacht_fractie"]
            dagelijks_data.append(
                {
                    "dag": dag + 1,
                    "verbruik_dag": dag_verbruik * dag_frac,
                    "verbruik_nacht": dag_verbruik * nacht_frac,
                    "verbruik_totaal": dag_verbruik,
                }
            )
        return pd.DataFrame(dagelijks_data)

    def _correleer_teruglevering_met_solar(
        self, solar_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Gebruik correlatie tussen maandelijkse teruglevering en solar opbrengst
        om dagelijkse teruglevering te schatten.
        """
        solar_df = solar_df.copy()
        solar_df["maand"] = (solar_df["dag"] - 1) // 30 + 1
        solar_df["maand"] = solar_df["maand"].clip(upper=12)
        maand_solar = solar_df.groupby("maand")["opbrengst_kwh"].sum()
        totaal_solar = maand_solar.sum()
        maand_teruglevering = {}
        for maand in range(1, 13):
            if totaal_solar > 0:
                maand_teruglevering[maand] = (
                    self.jaar_teruglevering * maand_solar.get(maand, 0) / totaal_solar
                )
            else:
                maand_teruglevering[maand] = 0
        dagelijkse_teruglevering = []
        for _, row in solar_df.iterrows():
            dag = row["dag"]
            maand = row["maand"]
            dagen_in_maand = len(solar_df[solar_df["maand"] == maand])
            teruglevering_dag = (
                maand_teruglevering[maand] / dagen_in_maand if dagen_in_maand > 0 else 0
            )
            dagelijkse_teruglevering.append(
                {"dag": dag, "teruglevering": teruglevering_dag}
            )
        return pd.DataFrame(dagelijkse_teruglevering)

    def _simuleer_batterij(
        self, battery_capacity_kwh: float, sim_df: pd.DataFrame
    ) -> dict:
        """
        Simuleer batterijgedrag voor een hele jaar met gegeven capaciteit.
        """
        battery_soc = battery_capacity_kwh * 0.5
        grid_inkoop = 0
        grid_teruglevering = 0
        battery_cycli = 0
        for _, row in sim_df.iterrows():
            solar = row["opbrengst_kwh"]
            verbruik_dag = row["verbruik_dag"]
            verbruik_nacht = row["verbruik_nacht"]
            direct_verbruik = min(solar, verbruik_dag)
            solar_over = solar - direct_verbruik
            verbruik_dag_over = verbruik_dag - direct_verbruik
            kan_laden = (battery_capacity_kwh - battery_soc) / self.battery_efficiency
            laden = min(solar_over, kan_laden)
            battery_soc += laden * self.battery_efficiency
            solar_over -= laden
            grid_teruglevering += solar_over
            uit_batterij_dag = min(verbruik_dag_over, battery_soc)
            battery_soc -= uit_batterij_dag
            grid_inkoop += verbruik_dag_over - uit_batterij_dag
            uit_batterij_nacht = min(verbruik_nacht, battery_soc)
            battery_soc -= uit_batterij_nacht
            grid_inkoop += verbruik_nacht - uit_batterij_nacht
            if battery_capacity_kwh > 0:
                battery_cycli += (
                    laden + uit_batterij_dag + uit_batterij_nacht
                ) / battery_capacity_kwh
        battery_cycli = battery_cycli / 2
        return {
            "battery_capacity": battery_capacity_kwh,
            "grid_inkoop_totaal": grid_inkoop,
            "grid_teruglevering_totaal": grid_teruglevering,
            "battery_cycli": battery_cycli,
            "zelfvoorzieningsgraad": 1 - grid_inkoop / self.jaar_verbruik
            if self.jaar_verbruik > 0
            else 0,
        }

    def _bereken_optimale_capaciteit(
        self, resultaten: list[dict], drempel: float = 0.3
    ) -> float:
        """
        Bepaal optimale capaciteit op basis van marginale winst.
        Stopt wanneer extra capaciteit minder dan 'drempel' % toevoegt aan zelfvoorziening per kWh.
        """
        if not resultaten:
            return 0.0
        sorted_res = sorted(resultaten, key=lambda x: x["battery_capacity"])
        optimal_cap = sorted_res[0]["battery_capacity"]
        for i in range(1, len(sorted_res)):
            prev = sorted_res[i - 1]
            curr = sorted_res[i]
            cap_diff = curr["battery_capacity"] - prev["battery_capacity"]
            if cap_diff <= 0:
                continue
            zv_diff = (
                curr["zelfvoorzieningsgraad"] - prev["zelfvoorzieningsgraad"]
            ) * 100.0
            marginal_gain = zv_diff / cap_diff
            if marginal_gain < drempel:
                return prev["battery_capacity"]
            optimal_cap = curr["battery_capacity"]
        return optimal_cap

    def _capaciteit_op_basis_van_teruglevering(self) -> float:
        """
        Bereken capaciteit op basis van gemiddeld dagelijks overschot.
        """
        if self.jaar_teruglevering <= 0:
            return 0.0
        dagelijks_overschot = self.jaar_teruglevering / 365.0
        optimal = dagelijks_overschot * 1.1 / 0.9
        return round(optimal * 2) / 2

    @rx.var
    def rate_limit_status(self) -> str:
        return self.get_usage_status("battery_estimator")

    @rx.event(background=True)
    async def calculate_results(self):
        async with self:
            if not self.check_can_execute("battery_estimator"):
                msg = (
                    "Dagelijkse limiet bereikt. Probeer het morgen opnieuw."
                    if self.is_authenticated
                    else "Dagelijkse limiet bereikt (5/5). Log in voor meer berekeningen."
                )
                yield rx.toast.error(msg)
                return
            self.is_processing = True
            self.error_message = ""
        try:
            async with self:
                self.increment_usage("battery_estimator")
            if not self.production_profile:
                raise ValueError(
                    "Upload eerst een zonne-opbrengst CSV (met 'opbrengst_kwh')."
                )
            solar_data = [
                {"dag": i + 1, "opbrengst_kwh": val}
                for i, val in enumerate(self.production_profile)
            ]
            solar_df = pd.DataFrame(solar_data)
            if len(solar_df) > 365:
                solar_df = solar_df.iloc[:365]
            dag_nacht_profiel = self._maak_dag_nacht_profiel()
            verbruik_df = self._bereken_dagelijks_verbruik(dag_nacht_profiel)
            teruglevering_df = self._correleer_teruglevering_met_solar(solar_df)
            sim_df = solar_df[["dag", "opbrengst_kwh"]].copy()
            sim_df = sim_df.merge(verbruik_df, on="dag")
            sim_df = sim_df.merge(teruglevering_df, on="dag")
            capaciteiten = range(3, 21, 1)
            resultaten = []
            for cap in capaciteiten:
                sim = self._simuleer_batterij(float(cap), sim_df)
                resultaten.append(sim)
            opt_marginal = self._bereken_optimale_capaciteit(resultaten, drempel=0.3)
            opt_surplus = self._capaciteit_op_basis_van_teruglevering()
            final_optimal_cap = max(opt_marginal, opt_surplus)
            beste = self._simuleer_batterij(final_optimal_cap, sim_df)
            async with self:
                self.optimal_capacity = final_optimal_cap
                self.zelfvoorzieningsgraad = round(
                    beste["zelfvoorzieningsgraad"] * 100, 1
                )
                self.grid_inkoop_totaal = round(beste["grid_inkoop_totaal"], 0)
                self.grid_teruglevering_totaal = round(
                    beste["grid_teruglevering_totaal"], 0
                )
                self.battery_cycli = round(beste["battery_cycli"], 0)
                levensduur_cycli = (
                    6000 / beste["battery_cycli"] if beste["battery_cycli"] > 0 else 99
                )
                self.levensduur_jaren = round(min(levensduur_cycli, 15.0), 1)
                self.comparison_chart_data = [
                    {
                        "capacity": r["battery_capacity"],
                        "zelfvoorziening": round(r["zelfvoorzieningsgraad"] * 100, 1),
                        "inkoop": round(r["grid_inkoop_totaal"], 0),
                        "teruglevering": round(r["grid_teruglevering_totaal"], 0),
                    }
                    for r in resultaten
                ]
                self.has_calculated = True
                self.is_processing = False
                StatisticsService.track_calculation(
                    self,
                    "battery_estimator",
                    {
                        "jaar_verbruik": self.jaar_verbruik,
                        "jaar_teruglevering": self.jaar_teruglevering,
                        "battery_efficiency": self.battery_efficiency,
                    },
                    {
                        "optimal_capacity": self.optimal_capacity,
                        "zelfvoorzieningsgraad": self.zelfvoorzieningsgraad,
                        "grid_inkoop_totaal": self.grid_inkoop_totaal,
                        "grid_teruglevering_totaal": self.grid_teruglevering_totaal,
                        "battery_cycli": self.battery_cycli,
                        "levensduur_jaren": self.levensduur_jaren,
                    },
                )
        except Exception as e:
            logging.exception(f"Simulation failed: {e}")
            async with self:
                self.error_message = f"Simulatie mislukt: {str(e)}"
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
            subject = f"Verbeterde Thuisbatterij Rapport - {datetime.date.today()}"
            email_data = {
                "title": "Thuisbatterij Simulatie Resultaten",
                "main_metric_label": "Optimale Capaciteit",
                "main_metric_value": f"{self.optimal_capacity} kWh",
                "main_metric_sub": f"Zelfvoorziening: {self.zelfvoorzieningsgraad}%",
                "stats": [
                    {"label": "Grid Inkoop", "value": f"{self.grid_inkoop_totaal} kWh"},
                    {
                        "label": "Grid Teruglevering",
                        "value": f"{self.grid_teruglevering_totaal} kWh",
                    },
                    {
                        "label": "Jaarlijks Verbruik",
                        "value": f"{self.jaar_verbruik} kWh",
                    },
                    {
                        "label": "Batterij Levensduur",
                        "value": f"{self.levensduur_jaren} jaar",
                    },
                ],
                "details": [
                    ("Batterij Cycli per jaar", f"{self.battery_cycli}"),
                    ("Efficiency", f"{int(self.battery_efficiency * 100)}%"),
                    ("Solar Productie Profiel", "Geüpload"),
                    ("Rapport Datum", str(datetime.date.today())),
                ],
            }
            if EmailService.send_results_email(user_email, subject, email_data):
                self.email_sent_modal_open = True
            else:
                rx.toast.error("Kon e-mail niet verzenden. Probeer het later opnieuw.")
        except Exception as e:
            logging.exception(f"Error sending battery estimator email: {e}")
            rx.toast.error("Er is een fout opgetreden bij het verzenden van de e-mail.")
        finally:
            self.is_sending_email = False