"""
CarbonZero GHG Protocol Calculation Engine.
Calculates Scope 1, Scope 2, and Scope 3 emissions according to standard international
GHG Protocol accounting methods and emission factors.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

# Standard emission factors (kg CO2e per unit)
# References: IPCC Guidelines, Central Electricity Authority (CEA) India, UK DEFRA, US EPA
EMISSION_FACTORS = {
    # Scope 1: Direct Combustion
    "diesel_generator_liters": 2.68,       # kg CO2e / L (Stationary combustion)
    "diesel_fleet_liters": 2.68,           # kg CO2e / L (Mobile diesel)
    "petrol_fleet_liters": 2.31,           # kg CO2e / L (Mobile petrol)
    "cng_fleet_kg": 1.88,                  # kg CO2e / kg (Mobile CNG)
    "lpg_canteen_kg": 1.51,                # kg CO2e / kg (Cooking & heating)
    
    # Scope 2: Indirect Emissions (Purchased Electricity)
    "grid_electricity_kwh": 0.713,         # kg CO2e / kWh (CEA National Grid Average)
    "solar_electricity_kwh": 0.02,         # kg CO2e / kWh (Solar PV Lifecycle emission)
    
    # Scope 3: Other Value Chain Indirect Emissions
    "employee_commute_pkm": 0.14,          # kg CO2e / passenger-km (Blended commuter traffic)
    "business_flight_pkm": 0.18,           # kg CO2e / passenger-km (Commercial aviation)
    "solid_waste_kg": 0.55,                # kg CO2e / kg (Landfill organic & mixed waste)
    "paper_consumption_kg": 0.92,          # kg CO2e / kg (Office paper lifecycle)
}


def compute_record_emissions(record: Dict[str, Any], custom_grid_factor: float = None) -> Dict[str, float]:
    """
    Computes emissions (in metric tonnes of CO2e) for a single record/row.
    """
    grid_factor = custom_grid_factor if custom_grid_factor is not None else EMISSION_FACTORS["grid_electricity_kwh"]
    
    # Scope 1 components (kg to tonnes: divide by 1000)
    s1_diesel_gen = (record.get("diesel_generator_liters", 0.0) * EMISSION_FACTORS["diesel_generator_liters"]) / 1000.0
    s1_diesel_fleet = (record.get("diesel_fleet_liters", 0.0) * EMISSION_FACTORS["diesel_fleet_liters"]) / 1000.0
    s1_petrol_fleet = (record.get("petrol_fleet_liters", 0.0) * EMISSION_FACTORS["petrol_fleet_liters"]) / 1000.0
    s1_cng_fleet = (record.get("cng_fleet_kg", 0.0) * EMISSION_FACTORS["cng_fleet_kg"]) / 1000.0
    s1_lpg = (record.get("lpg_canteen_kg", 0.0) * EMISSION_FACTORS["lpg_canteen_kg"]) / 1000.0
    
    scope_1_total = s1_diesel_gen + s1_diesel_fleet + s1_petrol_fleet + s1_cng_fleet + s1_lpg
    
    # Scope 2 components
    grid_kwh = record.get("grid_electricity_kwh", 0.0)
    solar_kwh = record.get("solar_electricity_kwh", 0.0)
    s2_grid = (grid_kwh * grid_factor) / 1000.0
    s2_solar = (solar_kwh * EMISSION_FACTORS["solar_electricity_kwh"]) / 1000.0
    scope_2_total = s2_grid + s2_solar
    
    # Scope 3 components
    s3_commute = (record.get("employee_commute_pkm", 0.0) * EMISSION_FACTORS["employee_commute_pkm"]) / 1000.0
    s3_flights = (record.get("business_flight_pkm", 0.0) * EMISSION_FACTORS["business_flight_pkm"]) / 1000.0
    s3_waste = (record.get("solid_waste_kg", 0.0) * EMISSION_FACTORS["solid_waste_kg"]) / 1000.0
    s3_paper = (record.get("paper_consumption_kg", 0.0) * EMISSION_FACTORS["paper_consumption_kg"]) / 1000.0
    scope_3_total = s3_commute + s3_flights + s3_waste + s3_paper
    
    total_co2e = scope_1_total + scope_2_total + scope_3_total
    
    return {
        "Scope_1_Generator": round(s1_diesel_gen, 3),
        "Scope_1_Fleet_Diesel": round(s1_diesel_fleet, 3),
        "Scope_1_Fleet_Petrol": round(s1_petrol_fleet, 3),
        "Scope_1_Fleet_CNG": round(s1_cng_fleet, 3),
        "Scope_1_LPG": round(s1_lpg, 3),
        "Scope_1_Total": round(scope_1_total, 3),
        
        "Scope_2_Grid": round(s2_grid, 3),
        "Scope_2_Solar": round(s2_solar, 3),
        "Scope_2_Total": round(scope_2_total, 3),
        
        "Scope_3_Commute": round(s3_commute, 3),
        "Scope_3_Flights": round(s3_flights, 3),
        "Scope_3_Waste": round(s3_waste, 3),
        "Scope_3_Paper": round(s3_paper, 3),
        "Scope_3_Total": round(scope_3_total, 3),
        
        "Total_CO2e_Tonnes": round(total_co2e, 3)
    }


def process_emissions_dataframe(df: pd.DataFrame, custom_grid_factor: float = None) -> pd.DataFrame:
    """
    Processes an entire DataFrame and appends emission columns.
    """
    results = []
    for _, row in df.iterrows():
        rec_emissions = compute_record_emissions(row.to_dict(), custom_grid_factor)
        results.append(rec_emissions)
        
    res_df = pd.DataFrame(results)
    return pd.concat([df.reset_index(drop=True), res_df], axis=1)


def get_emission_summary(processed_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Aggregates overall carbon footprint figures, percentages, and emission hotspots.
    """
    s1_total = float(processed_df["Scope_1_Total"].sum())
    s2_total = float(processed_df["Scope_2_Total"].sum())
    s3_total = float(processed_df["Scope_3_Total"].sum())
    grand_total = s1_total + s2_total + s3_total
    
    # Category detailed sums
    breakdown = {
        "Scope 1 - Diesel Generators": float(processed_df["Scope_1_Generator"].sum()),
        "Scope 1 - Fleet Diesel": float(processed_df["Scope_1_Fleet_Diesel"].sum()),
        "Scope 1 - Fleet Petrol": float(processed_df["Scope_1_Fleet_Petrol"].sum()),
        "Scope 1 - Fleet CNG": float(processed_df["Scope_1_Fleet_CNG"].sum()),
        "Scope 1 - Canteen LPG": float(processed_df["Scope_1_LPG"].sum()),
        "Scope 2 - Grid Electricity": float(processed_df["Scope_2_Grid"].sum()),
        "Scope 2 - Solar Power": float(processed_df["Scope_2_Solar"].sum()),
        "Scope 3 - Employee Commute": float(processed_df["Scope_3_Commute"].sum()),
        "Scope 3 - Business Travel (Flights)": float(processed_df["Scope_3_Flights"].sum()),
        "Scope 3 - Solid Waste": float(processed_df["Scope_3_Waste"].sum()),
        "Scope 3 - Paper Consumption": float(processed_df["Scope_3_Paper"].sum()),
    }
    
    # Sort categories to find top emission hotspots
    sorted_breakdown = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
    hotspots = [
        {"source": name, "emissions_tco2e": round(val, 2), "share_pct": round((val / grand_total * 100) if grand_total > 0 else 0, 1)}
        for name, val in sorted_breakdown if val > 0
    ]
    
    # Fleet emissions isolated
    fleet_emissions = (
        breakdown["Scope 1 - Fleet Diesel"] + 
        breakdown["Scope 1 - Fleet Petrol"] + 
        breakdown["Scope 1 - Fleet CNG"]
    )
    
    return {
        "grand_total_tco2e": round(grand_total, 2),
        "scope_1_tco2e": round(s1_total, 2),
        "scope_2_tco2e": round(s2_total, 2),
        "scope_3_tco2e": round(s3_total, 2),
        "scope_1_share_pct": round((s1_total / grand_total * 100) if grand_total > 0 else 0, 1),
        "scope_2_share_pct": round((s2_total / grand_total * 100) if grand_total > 0 else 0, 1),
        "scope_3_share_pct": round((s3_total / grand_total * 100) if grand_total > 0 else 0, 1),
        "fleet_emissions_tco2e": round(fleet_emissions, 2),
        "fleet_share_pct": round((fleet_emissions / grand_total * 100) if grand_total > 0 else 0, 1),
        "breakdown": breakdown,
        "hotspots": hotspots
    }
