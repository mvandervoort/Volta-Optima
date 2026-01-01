import math

SPECIFIC_HEAT_WATER_KWH_L_C = 4.186 / 3600
GAS_KWH_PER_M3 = 9.77
SOLAR_MONTHLY_WEIGHTS = {
    1: 0.03,
    2: 0.05,
    3: 0.08,
    4: 0.12,
    5: 0.13,
    6: 0.13,
    7: 0.13,
    8: 0.11,
    9: 0.1,
    10: 0.07,
    11: 0.03,
    12: 0.02,
}
DAYLIGHT_HOURS = {
    1: 8.0,
    2: 9.5,
    3: 12.0,
    4: 14.0,
    5: 16.0,
    6: 17.0,
    7: 16.5,
    8: 15.0,
    9: 12.5,
    10: 11.0,
    11: 9.0,
    12: 7.5,
}


def calculate_energy_demand(
    persons: int, liters_per_person: float, temp_cold: float, temp_hot: float
) -> dict:
    """
    Calculates daily and annual energy demand for hot water.
    """
    daily_liters = persons * liters_per_person
    delta_t = temp_hot - temp_cold
    daily_kwh = daily_liters * delta_t * SPECIFIC_HEAT_WATER_KWH_L_C
    annual_kwh = daily_kwh * 365
    return {
        "daily_liters": daily_liters,
        "daily_kwh": round(daily_kwh, 2),
        "annual_kwh": round(annual_kwh, 2),
    }


def calculate_solar_coverage(
    annual_energy_demand_kwh: float,
    efficiency_cop: float,
    annual_solar_surplus_kwh: float,
    heating_power_kw: float = 2.0,
) -> float:
    """
    Calculates how much of the energy demand input (electricity) can be covered by solar surplus.
    Takes into account monthly solar patterns, flat water demand, and heating capacity limits based on daylight hours.
    Returns kWh of input electricity covered by solar.
    """
    total_input_needed = annual_energy_demand_kwh / efficiency_cop
    covered_kwh = 0.0
    days_in_months = {
        1: 31,
        2: 28,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31,
    }
    for month in range(1, 13):
        solar_kwh_month = annual_solar_surplus_kwh * SOLAR_MONTHLY_WEIGHTS[month]
        demand_kwh_month = total_input_needed * (1 / 12)
        avg_daylight = DAYLIGHT_HOURS[month]
        usable_solar_hours = max(0.0, avg_daylight - 3.0)
        max_capturable_daily_kwh = usable_solar_hours * heating_power_kw
        max_capturable_month_kwh = max_capturable_daily_kwh * days_in_months[month]
        solar_available_capacity_limited = min(
            solar_kwh_month, max_capturable_month_kwh
        )
        usable = min(solar_available_capacity_limited, demand_kwh_month)
        covered_kwh += usable
    return covered_kwh


def calculate_gas_scenario(
    annual_demand_kwh: float,
    gas_price_m3: float,
    cv_efficiency: float,
    maintenance_yr: float,
    depreciation_yr: float,
) -> dict:
    """
    Calculates costs for Gas CV Kettle scenario.
    """
    input_kwh = annual_demand_kwh / cv_efficiency
    input_m3 = input_kwh / GAS_KWH_PER_M3
    energy_cost = input_m3 * gas_price_m3
    total_cost = energy_cost + maintenance_yr + depreciation_yr
    return {
        "input_m3": round(input_m3, 1),
        "input_kwh": round(input_kwh, 1),
        "energy_cost": round(energy_cost, 2),
        "total_cost": round(total_cost, 2),
        "maintenance": round(maintenance_yr, 2),
        "depreciation": round(depreciation_yr, 2),
        "solar_opportunity_cost": 0.0,
    }


def calculate_electric_scenario(
    annual_demand_kwh: float,
    elec_price_kwh: float,
    efficiency: float,
    maintenance_yr: float,
    purchase_price: float,
    lifespan_years: int,
    solar_surplus_kwh: float = 0,
    solar_enabled: bool = False,
    feedin_tariff: float = 0.08,
    standby_loss_kwh_day: float = 0.0,
    heating_power_kw: float = 2.0,
) -> dict:
    """
    Calculates costs for Electric Boiler scenario (Resistive).
    Includes logic for 'waterbatterij' (using solar surplus).

    UPDATED: Returns pure grid energy cost separately from opportunity cost.
    """
    depreciation_yr = purchase_price / lifespan_years if lifespan_years > 0 else 0
    standby_loss_annual = standby_loss_kwh_day * 365
    solar_covered_kwh = 0.0
    if solar_enabled:
        solar_covered_kwh = calculate_solar_coverage(
            annual_demand_kwh, efficiency, solar_surplus_kwh, heating_power_kw
        )
    total_input_kwh = annual_demand_kwh / efficiency + standby_loss_annual
    grid_kwh = max(0.0, total_input_kwh - solar_covered_kwh)
    energy_cost = grid_kwh * elec_price_kwh
    opportunity_cost = solar_covered_kwh * feedin_tariff
    total_cost = energy_cost + maintenance_yr + depreciation_yr
    grid_cost_baseline = total_input_kwh * elec_price_kwh
    total_cost_baseline = grid_cost_baseline + maintenance_yr + depreciation_yr
    waterbatterij_savings = max(0.0, total_cost_baseline - total_cost)
    effective_price = (
        energy_cost / total_input_kwh if total_input_kwh > 0 else elec_price_kwh
    )
    return {
        "input_kwh": round(total_input_kwh, 1),
        "grid_kwh": round(grid_kwh, 1),
        "solar_kwh": round(solar_covered_kwh, 1),
        "energy_cost": round(energy_cost, 2),
        "total_cost": round(total_cost, 2),
        "maintenance": round(maintenance_yr, 2),
        "depreciation": round(depreciation_yr, 2),
        "solar_coverage_pct": round(solar_covered_kwh / total_input_kwh * 100, 1)
        if total_input_kwh > 0
        else 0,
        "cost_without_solar": round(total_cost_baseline, 2),
        "waterbatterij_savings": round(waterbatterij_savings, 2),
        "effective_price_avg": round(effective_price, 3),
        "solar_opportunity_cost": round(opportunity_cost, 2),
    }


def calculate_heatpump_scenario(
    annual_demand_kwh: float,
    elec_price_kwh: float,
    cop: float,
    maintenance_yr: float,
    purchase_price: float,
    lifespan_years: int,
    solar_surplus_kwh: float = 0,
    solar_enabled: bool = False,
    feedin_tariff: float = 0.08,
    standby_loss_kwh_day: float = 0.0,
    heating_power_kw: float = 2.0,
) -> dict:
    """
    Calculates costs for Heat Pump Boiler scenario.
    Uses the same electric logic but with COP instead of efficiency.
    """
    return calculate_electric_scenario(
        annual_demand_kwh,
        elec_price_kwh,
        cop,
        maintenance_yr,
        purchase_price,
        lifespan_years,
        solar_surplus_kwh,
        solar_enabled,
        feedin_tariff,
        standby_loss_kwh_day,
        heating_power_kw,
    )