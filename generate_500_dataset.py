"""
Script to generate a 500-record comprehensive sustainability telemetry dataset
for CarbonZero AI Agent.
Columns adhere strictly to the GHG Protocol calculator schema.
"""

import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

def generate_500_records(output_path: str, seed: int = 42):
    np.random.seed(seed)
    
    start_date = datetime(2024, 1, 1)
    records = []
    
    for i in range(500):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        month_idx = current_date.month  # 1 to 12
        weekday = current_date.weekday() # 0-4 weekday, 5-6 weekend
        
        is_weekend = weekday >= 5
        # Activity reduction factor on weekends (30-40% of normal operational load)
        activity_multiplier = 0.35 if is_weekend else 1.0
        
        # Summer cooling load factor (May-August in northern hemisphere)
        summer_factor = 1.35 if month_idx in [5, 6, 7, 8] else (1.15 if month_idx in [3, 4, 9, 10] else 1.0)
        
        # Solar irradiation factor (higher in Feb-May, dips during monsoon July-August)
        solar_factor = 1.45 if month_idx in [2, 3, 4, 5] else (0.75 if month_idx in [7, 8] else 1.1)
        
        # 1. Grid Electricity (Daily kWh): Base ~3,200 kWh on weekdays
        base_grid = np.random.uniform(2900, 3500)
        grid_kwh = int((base_grid * summer_factor) * activity_multiplier + (800 if is_weekend else 0))
        
        # 2. Solar Generation (Daily kWh): Rooftop ~750 kWh base on sunny days
        base_solar = np.random.uniform(650, 920)
        solar_kwh = int(base_solar * solar_factor * np.random.uniform(0.85, 1.15))
        
        # 3. Diesel Generator Backup (Liters): Spikes during summer peak load or occasional outages
        if np.random.random() < 0.25:  # 25% chance of backup power run on any day
            dg_liters = int(np.random.uniform(40, 110) * summer_factor)
        else:
            dg_liters = int(np.random.uniform(5, 25))
            
        # 4. Campus Fleet (Liters/kg): Shuttles, vans, maintenance vehicles
        if is_weekend:
            diesel_fleet_l = int(np.random.uniform(25, 50))
            petrol_fleet_l = int(np.random.uniform(10, 25))
            cng_fleet_kg = int(np.random.uniform(5, 15))
        else:
            diesel_fleet_l = int(np.random.uniform(85, 130))
            petrol_fleet_l = int(np.random.uniform(35, 60))
            cng_fleet_kg = int(np.random.uniform(15, 28))
            
        # 5. Canteen LPG (kg)
        lpg_kg = int(np.random.uniform(8, 16) if is_weekend else np.random.uniform(22, 36))
        
        # 6. Scope 3: Commute passenger-km
        if is_weekend:
            commute_pkm = int(np.random.uniform(800, 1800))
        else:
            # Weekday commuting: ~5,500 to 7,500 passenger-km across student/staff pool
            commute_pkm = int(np.random.uniform(5500, 7800))
            
        # 7. Scope 3: Business flights (infrequent, occurring ~2-3 days a week)
        if np.random.random() < 0.35 and not is_weekend:
            flight_pkm = int(np.random.uniform(600, 2800))
        else:
            flight_pkm = 0
            
        # 8. Scope 3: Solid waste & Paper
        solid_waste = int(np.random.uniform(40, 80) if is_weekend else np.random.uniform(120, 190))
        paper_kg = int(np.random.uniform(3, 8) if is_weekend else np.random.uniform(15, 32))
        
        records.append({
            "Month": date_str,  # Maps directly to the temporal column expected by CarbonZero
            "grid_electricity_kwh": grid_kwh,
            "solar_electricity_kwh": solar_kwh,
            "diesel_generator_liters": dg_liters,
            "diesel_fleet_liters": diesel_fleet_l,
            "petrol_fleet_liters": petrol_fleet_l,
            "cng_fleet_kg": cng_fleet_kg,
            "lpg_canteen_kg": lpg_kg,
            "employee_commute_pkm": commute_pkm,
            "business_flight_pkm": flight_pkm,
            "solid_waste_kg": solid_waste,
            "paper_consumption_kg": paper_kg
        })
        
    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df)} rows to {output_path}")
    return df

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_file1 = os.path.join(base_dir, "campus_emissions_500_records.csv")
    out_file2 = os.path.join(base_dir, "data", "campus_emissions_500_records.csv")
    
    os.makedirs(os.path.dirname(out_file2), exist_ok=True)
    df = generate_500_records(out_file1)
    df.to_csv(out_file2, index=False)
    print("Files created successfully in both root and data/ directories.")
