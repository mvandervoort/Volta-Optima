import os
import logging
from typing import Optional
import requests
from requests.auth import HTTPBasicAuth
import datetime
from datetime import timedelta


class QuestDBClient:
    """
    Client for interacting with QuestDB via REST API.
    Handles time-series data ingestion and querying for energy metrics.
    """

    def __init__(self):
        self.host = os.getenv("QUESTDB_URL", "http://localhost:9000")
        self.username = os.getenv("QUESTDB_USERNAME")
        self.password = os.getenv("QUESTDB_PASSWORD")
        self.ingest_url = f"{self.host}/imp"
        self.query_url = f"{self.host}/exec"
        self.enabled = bool(self.host)
        self.auth = None
        if self.username and self.password:
            self.auth = HTTPBasicAuth(self.username, self.password)

    def ingest_metric(
        self,
        table: str,
        symbol: str,
        value: float,
        timestamp: Optional[datetime.datetime] = None,
    ) -> bool:
        """
        Ingest a single metric point via ILP (Influx Line Protocol) over HTTP.
        """
        if not self.enabled:
            logging.warning("QuestDB is disabled or missing credentials.")
            return False
        try:
            if timestamp is None:
                payload = f"{table},symbol={symbol} value={value}"
            else:
                ts_ns = int(timestamp.timestamp() * 1000000000.0)
                payload = f"{table},symbol={symbol} value={value} {ts_ns}"
            response = requests.post(self.ingest_url, data=payload, auth=self.auth)
            return response.status_code == 200
        except Exception as e:
            logging.exception(f"QuestDB Ingest Error: {e}")
            return False

    def query(self, sql: str) -> list[dict[str, object]]:
        """
        Execute a SQL query against QuestDB.
        """
        if not self.enabled:
            logging.warning("QuestDB is disabled or missing credentials.")
            return []
        try:
            response = requests.get(
                self.query_url, params={"query": sql}, auth=self.auth, timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if not data or "columns" not in data:
                    return []
                columns = [col["name"] for col in data["columns"]]
                dataset = data.get("dataset", [])
                results = []
                if dataset:
                    for row in dataset:
                        results.append(dict(zip(columns, row)))
                return results
            else:
                logging.error(f"QuestDB Query Failed: {response.text}")
                return []
        except Exception as e:
            logging.exception(f"QuestDB Query Error: {e}")
            return []

    def get_dynamic_pricing(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 168,
    ) -> list[dict[str, object]]:
        """
        Get hourly dynamic pricing data.
        If no dates provided, returns the most recent data limited by 'limit' (default 1 week).
        """
        where_clause = ""
        if start_date:
            where_clause += f" AND timestamp >= '{start_date}'"
        if end_date:
            where_clause += f" AND timestamp <= '{end_date}'"
        order_by = "ORDER BY timestamp DESC"
        if start_date and end_date:
            order_by = "ORDER BY timestamp ASC"
        sql = f"\n        SELECT timestamp, Supplier, EpexPrijs, Opslag, EnBel, NetVar, Subtotaal, BTW, Eindprijs\n        FROM dynamische_stroomprijzen_2024_Vattenfall\n        WHERE 1=1 {where_clause}\n        {order_by}\n        LIMIT {limit}\n        "
        return self.query(sql)

    def get_price_statistics(self, period: str = "year") -> dict[str, float]:
        """
        Get price statistics (min, max, avg).
        Period can be 'month', 'year', or 'all'.
        For 'year', it defaults to the full 2024 dataset.
        """
        where_clause = ""
        if period == "month":
            where_clause = (
                "WHERE timestamp >= '2024-12-01' AND timestamp <= '2024-12-31'"
            )
        elif period == "year":
            where_clause = (
                "WHERE timestamp >= '2024-01-01' AND timestamp <= '2024-12-31'"
            )
        sql = f"\n        SELECT \n            MIN(Eindprijs) as min_price, \n            MAX(Eindprijs) as max_price, \n            AVG(Eindprijs) as avg_price, \n            COUNT(*) as count\n        FROM dynamische_stroomprijzen_2024_Vattenfall\n        {where_clause}\n        "
        results = self.query(sql)
        if results:
            return results[0]
        return {"min_price": 0.0, "max_price": 0.0, "avg_price": 0.0, "count": 0}

    def get_price_components(self, start_date: str = "2024-01-01") -> dict[str, object]:
        """
        Get the average breakdown of price components since start_date.
        """
        sql = f"\n        SELECT \n            AVG(EpexPrijs) as avg_epex, \n            AVG(Opslag) as avg_markup, \n            AVG(EnBel) as avg_tax, \n            AVG(NetVar) as avg_network, \n            AVG(BTW) as avg_vat, \n            AVG(Eindprijs) as avg_total \n        FROM dynamische_stroomprijzen_2024_Vattenfall\n        WHERE timestamp >= '{start_date}'\n        "
        results = self.query(sql)
        if results:
            data = results[0]
            total = data.get("avg_total", 1.0)
            if total == 0:
                total = 1.0
            return {
                "components": {
                    "EPEX Spot": data.get("avg_epex", 0),
                    "Markup": data.get("avg_markup", 0),
                    "Energy Tax": data.get("avg_tax", 0),
                    "Network Fee": data.get("avg_network", 0),
                    "VAT": data.get("avg_vat", 0),
                },
                "percentages": {
                    "EPEX Spot": (data.get("avg_epex", 0) or 0) / total * 100,
                    "Markup": (data.get("avg_markup", 0) or 0) / total * 100,
                    "Energy Tax": (data.get("avg_tax", 0) or 0) / total * 100,
                    "Network Fee": (data.get("avg_network", 0) or 0) / total * 100,
                    "VAT": (data.get("avg_vat", 0) or 0) / total * 100,
                },
                "total": total,
            }
        return {}

    def get_peak_offpeak_comparison(self) -> dict[str, float]:
        """
        Compare peak (7am-11pm) vs off-peak (11pm-7am) prices.
        """
        sql = """
        SELECT 
            AVG(CASE WHEN hour(timestamp) >= 7 AND hour(timestamp) < 23 THEN Eindprijs END) as peak_price, 
            AVG(CASE WHEN hour(timestamp) < 7 OR hour(timestamp) >= 23 THEN Eindprijs END) as offpeak_price 
        FROM dynamische_stroomprijzen_2024_Vattenfall
        """
        results = self.query(sql)
        if results:
            return results[0]
        return {"peak_price": 0.0, "offpeak_price": 0.0}

    def get_hourly_energy_data(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict[str, object]]:
        """
        Get hourly energy consumption/generation data for a user.
        This assumes table 'hourly_energy_data' exists with columns like timestamp, user_id, consumption_kwh, production_kwh
        """
        where_clause = f"WHERE user_id = '{user_id}'"
        if start_date:
            where_clause += f" AND timestamp >= '{start_date}'"
        if end_date:
            where_clause += f" AND timestamp <= '{end_date}'"
        sql = f"\n        SELECT timestamp, consumption_kwh, production_kwh\n        FROM hourly_energy_data\n        {where_clause}\n        ORDER BY timestamp ASC\n        "
        return self.query(sql)

    def calculate_savings_with_battery(
        self,
        annual_consumption: float,
        solar_production: float,
        battery_capacity_kwh: float,
    ) -> dict[str, float]:
        """
        Simulate battery savings based on dynamic pricing data and estimated load profiles.
        Uses actual 2024 pricing data from QuestDB.
        """
        stats = self.get_price_statistics(period="year")
        avg_price = stats.get("avg_price", 0.38)
        sql_spread = """
        SELECT AVG(spread) as avg_spread FROM (
            SELECT timestamp, MAX(Eindprijs) - MIN(Eindprijs) as spread 
            FROM dynamische_stroomprijzen_2024_Vattenfall 
            SAMPLE BY 1d ALIGN TO CALENDAR
        )
        """
        spread_res = self.query(sql_spread)
        avg_spread = 0.15
        if spread_res and spread_res[0].get("avg_spread"):
            avg_spread = spread_res[0]["avg_spread"]
        base_cost = annual_consumption * avg_price
        direct_consumption_ratio = 0.3
        direct_savings = solar_production * direct_consumption_ratio * avg_price
        battery_boost_ratio = min(0.4, battery_capacity_kwh * 250 / annual_consumption)
        battery_savings = solar_production * battery_boost_ratio * avg_price
        arbitrage_cycles = 200
        arbitrage_savings = battery_capacity_kwh * arbitrage_cycles * avg_spread
        total_savings = direct_savings + battery_savings + arbitrage_savings
        new_bill = max(0, base_cost - total_savings)
        return {
            "annual_cost_no_solar": round(base_cost, 2),
            "annual_cost_with_system": round(new_bill, 2),
            "total_annual_savings": round(total_savings, 2),
            "battery_added_value": round(battery_savings + arbitrage_savings, 2),
            "self_sufficiency_increase": round(battery_boost_ratio * 100, 1),
            "avg_price_used": round(avg_price, 4),
            "avg_spread_used": round(avg_spread, 4),
        }

    def get_aggregated_energy(
        self, symbol: str, interval: str = "1d"
    ) -> list[dict[str, object]]:
        """
        Get aggregated energy data for a specific symbol.
        Interval examples: '1h', '1d', '30d'
        """
        sql = f"\n        SELECT timestamp, sum(value) as total_energy\n        FROM energy_metrics\n        WHERE symbol = '{symbol}'\n        SAMPLE BY {interval} ALIGN TO CALENDAR\n        ORDER BY timestamp DESC\n        LIMIT 100\n        "
        return self.query(sql)