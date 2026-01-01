import reflex as rx
import asyncio
import datetime
from app.states.base_state import State
from app.utils.warmwater_calculations import (
    calculate_energy_demand,
    calculate_gas_scenario,
    calculate_electric_scenario,
    calculate_heatpump_scenario,
)
from app.services.email_service import EmailService
from app.services.statistics_service import StatisticsService
import logging


class WarmWaterState(State):
    persons: int = 3
    liters_per_person: float = 50.0
    direct_kwh_annual: str = ""
    section_verbruik_open: bool = True
    section_gas_open: bool = False
    section_boiler_open: bool = False
    section_wp_open: bool = False
    section_price_open: bool = False
    gas_price: float = 1.2
    electricity_price: float = 0.3
    feedin_tariff: float = 0.08
    cv_efficiency: float = 0.85
    gas_maintenance: float = 50.0
    gas_depreciation: float = 100.0
    boiler_purchase_price: float = 600.0
    boiler_efficiency: float = 0.98
    boiler_maintenance: float = 20.0
    boiler_lifespan: int = 15
    waterbatterij_enabled: bool = False
    boiler_heating_power: float = 2.0
    wpboiler_purchase_price: float = 2200.0
    cop: float = 3.0
    wpboiler_maintenance: float = 50.0
    wpboiler_lifespan: int = 15
    wpboiler_waterbatterij_enabled: bool = False
    wpboiler_heating_power: float = 2.0
    annual_solar_surplus: float = 2000.0
    boiler_standby_loss: float = 0.8
    wpboiler_standby_loss: float = 0.5
    has_calculated: bool = False
    is_processing: bool = False
    is_sending_email: bool = False
    demand_results: dict[str, float] = {}
    gas_results: dict[str, float] = {}
    boiler_results: dict[str, float] = {}
    wp_results: dict[str, float] = {}
    comparison_results: list[dict[str, str]] = []
    bar_chart_data: list[dict] = []
    cheapest_option: str = ""
    email_sent_modal_open: bool = False
    intro_content: dict[str, str] = {
        "title": "Warmwater Calculator",
        "subtitle": "Vergelijk kosten van verschillende warmwatersystemen voor uw huishouden.",
        "instructions": """
<p>De Warmwater Calculator helpt u de meest kostenefficiënte oplossing te vinden voor uw warmwatervoorziening. Vergelijk de jaarlijkse kosten van een gasketel, elektrische boiler of warmtepompboiler.</p>
""",
    }
    technical_details_content: dict[str, str] = {
        "title": "Technische Achtergrond & Berekeningen",
        "content": """
<h3 class="text-lg font-semibold text-gray-800 mb-2">Warmwaterbehoefte Berekening</h3>
<p class="mb-4">De warmwaterbehoefte wordt berekend op basis van het aantal personen en hun douchegedrag. Standaard wordt uitgegaan van 50 liter warm water per douche.</p>
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
            module_data = directus.get_advice_module("warm-water")
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
            logging.exception(f"Error loading warm-water content: {e}")

    @rx.event
    def close_email_modal(self):
        self.email_sent_modal_open = False

    @rx.var
    def gas_energy_cost(self) -> float:
        return self.gas_results.get("energy_cost", 0.0)

    @rx.var
    def boiler_energy_cost(self) -> float:
        return self.boiler_results.get("energy_cost", 0.0)

    @rx.var
    def wp_energy_cost(self) -> float:
        return self.wp_results.get("energy_cost", 0.0)

    @rx.var
    def boiler_opportunity_cost(self) -> float:
        return self.boiler_results.get("solar_opportunity_cost", 0.0)

    @rx.var
    def wp_opportunity_cost(self) -> float:
        return self.wp_results.get("solar_opportunity_cost", 0.0)

    @rx.var
    def gas_maintenance_cost(self) -> float:
        return self.gas_results.get("maintenance", 0.0)

    @rx.var
    def boiler_maintenance_cost(self) -> float:
        return self.boiler_results.get("maintenance", 0.0)

    @rx.var
    def wp_maintenance_cost(self) -> float:
        return self.wp_results.get("maintenance", 0.0)

    @rx.var
    def gas_depreciation_cost(self) -> float:
        return self.gas_results.get("depreciation", 0.0)

    @rx.var
    def boiler_depreciation(self) -> float:
        return self.boiler_results.get("depreciation", 0.0)

    @rx.var
    def wp_depreciation(self) -> float:
        return self.wp_results.get("depreciation", 0.0)

    @rx.var
    def gas_total(self) -> float:
        return self.gas_results.get("total_cost", 0.0)

    @rx.var
    def boiler_total(self) -> float:
        return self.boiler_results.get("total_cost", 0.0)

    @rx.var
    def wp_total(self) -> float:
        return self.wp_results.get("total_cost", 0.0)

    @rx.var
    def boiler_solar_kwh(self) -> float:
        return self.boiler_results.get("solar_kwh", 0.0)

    @rx.var
    def wp_solar_kwh(self) -> float:
        return self.wp_results.get("solar_kwh", 0.0)

    @rx.var
    def boiler_unused_surplus(self) -> float:
        return round(
            self.annual_solar_surplus - self.boiler_results.get("solar_kwh", 0.0), 1
        )

    @rx.var
    def wp_unused_surplus(self) -> float:
        return round(
            self.annual_solar_surplus - self.wp_results.get("solar_kwh", 0.0), 1
        )

    @rx.event
    def toggle_section(self, section: str):
        if section == "verbruik":
            self.section_verbruik_open = not self.section_verbruik_open
        elif section == "gas":
            self.section_gas_open = not self.section_gas_open
        elif section == "boiler":
            self.section_boiler_open = not self.section_boiler_open
        elif section == "wp":
            self.section_wp_open = not self.section_wp_open
        elif section == "price":
            self.section_price_open = not self.section_price_open

    @rx.event
    def set_direct_kwh_annual(self, val: str):
        self.direct_kwh_annual = val

    @rx.event
    def set_persons(self, val: str):
        self.persons = int(val) if val else 0

    @rx.event
    def set_liters_per_person(self, val: str):
        self.liters_per_person = float(val) if val else 0.0

    @rx.event
    def set_gas_price(self, val: str):
        self.gas_price = float(val) if val else 0.0

    @rx.event
    def set_electricity_price(self, val: str):
        self.electricity_price = float(val) if val else 0.0

    @rx.event
    def set_feedin_tariff(self, val: str):
        self.feedin_tariff = float(val) if val else 0.0

    @rx.event
    def set_cv_efficiency(self, val: str):
        self.cv_efficiency = float(val) if val else 0.0

    @rx.event
    def set_gas_maintenance(self, val: str):
        self.gas_maintenance = float(val) if val else 0.0

    @rx.event
    def set_gas_depreciation(self, val: str):
        self.gas_depreciation = float(val) if val else 0.0

    @rx.event
    def set_boiler_purchase_price(self, val: str):
        self.boiler_purchase_price = float(val) if val else 0.0

    @rx.event
    def set_boiler_efficiency(self, val: str):
        self.boiler_efficiency = float(val) if val else 0.0

    @rx.event
    def set_boiler_maintenance(self, val: str):
        self.boiler_maintenance = float(val) if val else 0.0

    @rx.event
    def set_boiler_lifespan(self, val: str):
        self.boiler_lifespan = int(val) if val else 0

    @rx.event
    def set_boiler_heating_power(self, val: str):
        self.boiler_heating_power = float(val) if val else 0.0

    @rx.event
    def set_wpboiler_purchase_price(self, val: str):
        self.wpboiler_purchase_price = float(val) if val else 0.0

    @rx.event
    def set_cop(self, val: str):
        self.cop = float(val) if val else 0.0

    @rx.event
    def set_wpboiler_maintenance(self, val: str):
        self.wpboiler_maintenance = float(val) if val else 0.0

    @rx.event
    def set_wpboiler_lifespan(self, val: str):
        self.wpboiler_lifespan = int(val) if val else 0

    @rx.event
    def set_wpboiler_heating_power(self, val: str):
        self.wpboiler_heating_power = float(val) if val else 0.0

    @rx.event
    def set_annual_solar_surplus(self, val: str):
        self.annual_solar_surplus = float(val) if val else 0.0

    @rx.event
    def set_boiler_standby_loss(self, val: str):
        self.boiler_standby_loss = float(val) if val else 0.0

    @rx.event
    def set_wpboiler_standby_loss(self, val: str):
        self.wpboiler_standby_loss = float(val) if val else 0.0

    @rx.event
    def toggle_waterbatterij(self):
        self.waterbatterij_enabled = not self.waterbatterij_enabled
        if self.waterbatterij_enabled:
            self.boiler_purchase_price = 1000.0
        else:
            self.boiler_purchase_price = 600.0

    @rx.event
    def toggle_wp_waterbatterij(self):
        self.wpboiler_waterbatterij_enabled = not self.wpboiler_waterbatterij_enabled
        if self.wpboiler_waterbatterij_enabled:
            self.wpboiler_purchase_price = 2800.0
        else:
            self.wpboiler_purchase_price = 2200.0

    @rx.var
    def rate_limit_status(self) -> str:
        return self.get_usage_status("warm_water")

    @rx.event(background=True)
    async def calculate_results(self):
        async with self:
            if not self.check_can_execute("warm_water"):
                msg = (
                    "Dagelijkse limiet bereikt. Probeer het morgen opnieuw."
                    if self.is_authenticated
                    else "Dagelijkse limiet bereikt (5/5). Log in voor meer berekeningen."
                )
                yield rx.toast.error(msg)
                return
            self.is_processing = True
            self.increment_usage("warm_water")
        TEMP_COLD = 10.0
        TEMP_HOT = 60.0
        if self.direct_kwh_annual and float(self.direct_kwh_annual) > 0:
            annual_kwh = float(self.direct_kwh_annual)
            demand = {
                "daily_liters": 0,
                "daily_kwh": round(annual_kwh / 365.0, 2),
                "annual_kwh": annual_kwh,
            }
        else:
            demand = calculate_energy_demand(
                self.persons, self.liters_per_person, TEMP_COLD, TEMP_HOT
            )
        gas_calc = calculate_gas_scenario(
            demand["annual_kwh"],
            self.gas_price,
            self.cv_efficiency,
            self.gas_maintenance,
            self.gas_depreciation,
        )
        elec_calc = calculate_electric_scenario(
            demand["annual_kwh"],
            self.electricity_price,
            self.boiler_efficiency,
            self.boiler_maintenance,
            self.boiler_purchase_price,
            self.boiler_lifespan,
            solar_surplus_kwh=self.annual_solar_surplus,
            solar_enabled=self.waterbatterij_enabled,
            feedin_tariff=self.feedin_tariff,
            standby_loss_kwh_day=self.boiler_standby_loss,
            heating_power_kw=self.boiler_heating_power,
        )
        wp_calc = calculate_heatpump_scenario(
            demand["annual_kwh"],
            self.electricity_price,
            self.cop,
            self.wpboiler_maintenance,
            self.wpboiler_purchase_price,
            self.wpboiler_lifespan,
            solar_surplus_kwh=self.annual_solar_surplus,
            solar_enabled=self.wpboiler_waterbatterij_enabled,
            feedin_tariff=self.feedin_tariff,
            standby_loss_kwh_day=self.wpboiler_standby_loss,
            heating_power_kw=self.wpboiler_heating_power,
        )
        costs = [
            ("Gas CV", gas_calc["total_cost"]),
            ("Elektrische Boiler", elec_calc["total_cost"]),
            ("Warmtepompboiler", wp_calc["total_cost"]),
        ]
        costs.sort(key=lambda x: x[1])
        cheapest = costs[0][0]
        comp_results = []
        baseline_cost = gas_calc["total_cost"]
        for name, cost in costs:
            diff = baseline_cost - cost
            status = "Duurder" if diff < 0 else "Goedkoper"
            extra_info = ""
            if name == "Elektrische Boiler" and self.waterbatterij_enabled:
                savings = elec_calc.get("waterbatterij_savings", 0)
                if savings > 0:
                    extra_info = f" (Incl. €{savings:.0f} waterbatterij voordeel)"
            elif name == "Warmtepompboiler" and self.wpboiler_waterbatterij_enabled:
                savings = wp_calc.get("waterbatterij_savings", 0)
                if savings > 0:
                    extra_info = f" (Incl. €{savings:.0f} waterbatterij voordeel)"
            comp_results.append(
                {
                    "name": name,
                    "cost": f"€{cost:.2f}",
                    "diff": f"{status} (€{abs(diff):.2f})",
                    "is_cheapest": name == cheapest,
                    "extra_info": extra_info,
                }
            )
        chart_data = [
            {
                "name": "Jaarkosten",
                "Huidig (Gas)": gas_calc["total_cost"],
                "Elektrische Boiler": elec_calc["total_cost"],
                "Warmtepompboiler": wp_calc["total_cost"],
            }
        ]
        await asyncio.sleep(0.5)
        async with self:
            self.demand_results = demand
            self.gas_results = gas_calc
            self.boiler_results = elec_calc
            self.wp_results = wp_calc
            self.comparison_results = comp_results
            self.bar_chart_data = chart_data
            self.cheapest_option = cheapest
            self.has_calculated = True
            self.is_processing = False
            StatisticsService.track_calculation(
                self,
                "warm_water",
                {
                    "persons": self.persons,
                    "liters_per_person": self.liters_per_person,
                    "gas_price": self.gas_price,
                    "electricity_price": self.electricity_price,
                    "cop": self.cop,
                    "waterbatterij_enabled": self.waterbatterij_enabled,
                    "wpboiler_waterbatterij_enabled": self.wpboiler_waterbatterij_enabled,
                },
                {
                    "gas_total": self.gas_results.get("total_cost", 0.0),
                    "boiler_total": self.boiler_results.get("total_cost", 0.0),
                    "wp_total": self.wp_results.get("total_cost", 0.0),
                    "cheapest_option": self.cheapest_option,
                },
            )

    @rx.event
    async def email_results(self):
        if not self.is_authenticated or not self.user:
            yield rx.toast.error("U moet ingelogd zijn om resultaten te mailen.")
            return
        self.is_sending_email = True
        yield
        try:
            user_email = self.user.get("email")
            subject = f"Warm Tapwater Advies - {datetime.date.today()}"
            min_cost = 0.0
            if self.gas_results and self.boiler_results and self.wp_results:
                min_cost = min(
                    self.gas_results.get("total_cost", 0),
                    self.boiler_results.get("total_cost", 0),
                    self.wp_results.get("total_cost", 0),
                )
            email_data = {
                "title": "Warm Water Scan Resultaten",
                "main_metric_label": "Goedkoopste Optie",
                "main_metric_value": self.cheapest_option,
                "main_metric_sub": f"Jaarkosten: €{min_cost:.2f}",
                "stats": [
                    {
                        "label": "Gas Jaarkosten",
                        "value": f"€{self.gas_results.get('total_cost', 0):.2f}",
                    },
                    {
                        "label": "E-Boiler Jaarkosten",
                        "value": f"€{self.boiler_results.get('total_cost', 0):.2f}",
                    },
                    {
                        "label": "WP-Boiler Jaarkosten",
                        "value": f"€{self.wp_results.get('total_cost', 0):.2f}",
                    },
                    {
                        "label": "Jaarlijks Verbruik",
                        "value": f"{self.demand_results.get('annual_kwh', 0)} kWh",
                    },
                ],
                "details": [
                    ("Huishouden", f"{self.persons} personen"),
                    ("Verbruik per persoon", f"{self.liters_per_person} liter/dag"),
                    (
                        "Solar Surplus Gebruikt (WP)",
                        f"{self.wp_results.get('solar_kwh', 0)} kWh",
                    ),
                    (
                        "Gemiste Teruglevering (WP)",
                        f"€{self.wp_results.get('solar_opportunity_cost', 0):.2f}",
                    ),
                    ("COP Warmtepomp", str(self.cop)),
                ],
            }
            if EmailService.send_results_email(user_email, subject, email_data):
                self.email_sent_modal_open = True
            else:
                rx.toast.error("Kon e-mail niet verzenden. Probeer het later opnieuw.")
        except Exception as e:
            logging.exception(f"Error sending warm water email: {e}")
            rx.toast.error("Er is een fout opgetreden bij het verzenden van de e-mail.")
        finally:
            self.is_sending_email = False