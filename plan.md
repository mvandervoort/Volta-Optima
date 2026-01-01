# Contract Vergelijking Prototype - Implementation Plan

## Overview
Build a contract comparison tool that calculates annual energy costs for 3 contract types (Fixed, Variable, Dynamic) based on uploaded consumption and solar production profiles, using real 2024 hourly pricing data from QuestDB.

---

## Phase 1: State & Data Infrastructure ✅
- [x] Create ContractComparisonState with all required state variables
- [x] Add CSV upload handlers for consumption and production profiles
- [x] Add input fields for fixed/variable contract prices (purchase + feed-in)
- [x] Implement QuestDB integration for dynamic pricing data retrieval

---

## Phase 2: Core Calculation Logic ✅
- [x] Implement hourly netto calculation (consumption - production per hour)
- [x] Calculate costs for Fixed contract (simple: netto * fixed_price, teruglevering * fixed_feedin)
- [x] Calculate costs for Variable contract (same logic, different prices)
- [x] Calculate costs for Dynamic contract (hourly prices from QuestDB, price at T = price for hour T+1)
- [x] Generate comparison results with annual totals and savings breakdown

---

## Phase 3: UI & Results Display ✅
- [x] Build form UI with 2 upload zones (consumption CSV, production CSV)
- [x] Add input fields for fixed/variable prices (inkoop + teruglevering)
- [x] Create results display with comparison cards for all 3 contract types
- [x] Add charts showing cost breakdown and monthly comparison
- [x] Wire up the page to the existing route /tools/contract-vergelijking

---

## Test Results
- Consumption: 5901 kWh/jaar
- Solar Production: 1665 kWh/jaar
- Fixed Contract: €1807.55/jaar
- Variable Contract: €1581.61/jaar (goedkoopst)
- Dynamic Contract: €1700.61/jaar

## Data Notes
- CSV files in assets: `ETAP-huisverbruik-profiel-1y-1h.csv`, `ETAP-stroomopwekking-solar-1y-1h.csv`
- QuestDB table: `dyn_stroom_prijzen` with column `Eindprijs` (8760 hourly prices for 2024)
- Price timing: Price at timestamp T is the price for the FOLLOWING hour (T to T+1)
