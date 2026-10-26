"""
CarbonZero EV Fleet Transition & Solar Microgrid Simulator.
Models the technical, carbon, and financial impact of transitioning an institutional
or corporate vehicle fleet from Internal Combustion Engines (ICE) to Electric Vehicles (EVs).
"""

from typing import Dict, Any

def simulate_ev_transition(
    total_ice_vehicles: int = 30,
    electrification_pct: float = 60.0,
    avg_annual_km_per_vehicle: float = 24000.0,
    current_fuel_price_per_liter: float = 95.0,        # in currency units (e.g., INR or normalized)
    ice_fuel_economy_km_per_liter: float = 12.0,
    ev_efficiency_kwh_per_km: float = 0.18,            # 18 kWh / 100 km typical passenger/light van
    electricity_cost_per_kwh: float = 7.5,             # commercial grid tariff
    solar_charging_share_pct: float = 40.0,            # % of EV charging powered by solar PV
    solar_lcoe_per_kwh: float = 2.8,                   # Levelized cost of rooftop solar
    grid_emission_factor_kg_per_kwh: float = 0.713,
    avg_ev_vehicle_cost: float = 1400000.0,            # avg replacement/purchase cost per EV
    ice_annual_maintenance_per_vehicle: float = 35000.0,
    ev_annual_maintenance_per_vehicle: float = 18000.0, # ~48% reduction in maintenance
    charger_ac_cost: float = 65000.0,                  # 7.4 kW - 22 kW Level 2 AC charger
    charger_dc_fast_cost: float = 450000.0,            # 30 kW - 60 kW DC Fast charger
    government_incentive_per_ev: float = 150000.0       # subsidy / tax benefit
) -> Dict[str, Any]:
    """
    Executes a comprehensive techno-economic and carbon abatement simulation.
    """
    ev_count = int(round(total_ice_vehicles * (electrification_pct / 100.0)))
    if ev_count == 0:
        return {
            "ev_count": 0,
            "electrification_pct": electrification_pct,
            "annual_co2_saved_tco2e": 0.0,
            "annual_fuel_saved_liters": 0.0,
            "annual_fuel_cost_saved": 0.0,
            "annual_ev_electricity_kwh": 0.0,
            "annual_charging_cost": 0.0,
            "annual_maintenance_savings": 0.0,
            "net_annual_savings": 0.0,
            "total_capex": 0.0,
            "payback_years": 0.0,
            "ac_chargers_needed": 0,
            "dc_chargers_needed": 0,
            "solar_carbon_benefit_tco2e": 0.0
        }

    # 1. Operational Distance & Fuel Replaced
    annual_km_electrified = ev_count * avg_annual_km_per_vehicle
    fuel_liters_avoided = annual_km_electrified / ice_fuel_economy_km_per_liter
    fuel_cost_saved = fuel_liters_avoided * current_fuel_price_per_liter
    
    # Baseline ICE emissions (diesel/petrol blended ~2.5 kg CO2e/L)
    baseline_ice_co2_kg = fuel_liters_avoided * 2.50
    
    # 2. EV Electricity Demand & Charging
    total_ev_kwh_needed = annual_km_electrified * ev_efficiency_kwh_per_km
    solar_kwh = total_ev_kwh_needed * (solar_charging_share_pct / 100.0)
    grid_kwh = total_ev_kwh_needed - solar_kwh
    
    # Charging costs
    charging_cost_grid = grid_kwh * electricity_cost_per_kwh
    charging_cost_solar = solar_kwh * solar_lcoe_per_kwh
    total_charging_cost = charging_cost_grid + charging_cost_solar
    
    # EV charging emissions
    # Solar emissions: ~0.02 kg/kWh, Grid: grid_emission_factor_kg_per_kwh
    ev_co2_grid_kg = grid_kwh * grid_emission_factor_kg_per_kwh
    ev_co2_solar_kg = solar_kwh * 0.02
    total_ev_co2_kg = ev_co2_grid_kg + ev_co2_solar_kg
    
    # Net Carbon Saved (in metric tonnes)
    net_co2_saved_kg = baseline_ice_co2_kg - total_ev_co2_kg
    annual_co2_saved_tco2e = max(0.0, net_co2_saved_kg / 1000.0)
    
    # Solar benefit vs pure grid charging
    pure_grid_co2_kg = total_ev_kwh_needed * grid_emission_factor_kg_per_kwh
    solar_benefit_tco2e = max(0.0, (pure_grid_co2_kg - total_ev_co2_kg) / 1000.0)
    
    # 3. Maintenance Savings
    ice_maintenance_cost = ev_count * ice_annual_maintenance_per_vehicle
    ev_maintenance_cost = ev_count * ev_annual_maintenance_per_vehicle
    maintenance_savings = ice_maintenance_cost - ev_maintenance_cost
    
    # 4. Total Net Operating Savings
    net_annual_savings = (fuel_cost_saved + maintenance_savings) - total_charging_cost
    
    # 5. Charging Infrastructure Sizing
    # Typically 1 AC dual-gun charger per 3 EVs, and 1 DC fast charger per 15 EVs
    ac_chargers = max(1, int(np.ceil(ev_count / 3.0)))
    dc_chargers = max(0, int(np.floor(ev_count / 15.0)))
    
    infra_capex = (ac_chargers * charger_ac_cost) + (dc_chargers * charger_dc_fast_cost)
    vehicle_gross_capex = ev_count * avg_ev_vehicle_cost
    incentives_total = ev_count * government_incentive_per_ev
    net_capex = (vehicle_gross_capex - incentives_total) + infra_capex
    
    # 6. Financial Payback
    payback_years = round(net_capex / net_annual_savings, 1) if net_annual_savings > 0 else 99.9
    
    # 7. ROI over 8-year battery life
    eight_year_savings = (net_annual_savings * 8) - net_capex
    roi_8yr_pct = round((eight_year_savings / net_capex * 100), 1) if net_capex > 0 else 0.0
    
    return {
        "ev_count": ev_count,
        "total_ice_vehicles": total_ice_vehicles,
        "electrification_pct": electrification_pct,
        "annual_co2_saved_tco2e": round(annual_co2_saved_tco2e, 2),
        "co2_reduction_pct": round((net_co2_saved_kg / baseline_ice_co2_kg * 100) if baseline_ice_co2_kg > 0 else 0, 1),
        "annual_fuel_saved_liters": round(fuel_liters_avoided, 1),
        "annual_fuel_cost_saved": round(fuel_cost_saved, 2),
        "annual_ev_electricity_kwh": round(total_ev_kwh_needed, 1),
        "annual_charging_cost": round(total_charging_cost, 2),
        "annual_maintenance_savings": round(maintenance_savings, 2),
        "net_annual_savings": round(net_annual_savings, 2),
        "ac_chargers_needed": ac_chargers,
        "dc_chargers_needed": dc_chargers,
        "infra_capex": round(infra_capex, 2),
        "net_capex": round(net_capex, 2),
        "payback_years": payback_years,
        "roi_8yr_pct": roi_8yr_pct,
        "solar_carbon_benefit_tco2e": round(solar_benefit_tco2e, 2)
    }

import numpy as np
