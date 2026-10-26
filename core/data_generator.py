"""
Sample Data Generator for CarbonZero.
Generates realistic 12-month sustainability telemetry for an enterprise or academic campus.
"""

import os
from typing import Optional
import pandas as pd
import numpy as np

def generate_campus_sample_data(seed: int = 42) -> pd.DataFrame:
    """
    Creates a realistic 12-month dataset of resource usage and activity data.
    """
    np.random.seed(seed)
    
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    data = []
    for i, month in enumerate(months):
        # Summer cooling load factor (May-August higher electricity)
        cooling_factor = 1.35 if i in [3, 4, 5, 6] else (1.15 if i in [2, 7, 8] else 1.0)
        
        # Grid electricity: baseline ~90,000 kWh
        grid_kwh = int(np.random.uniform(85000, 105000) * cooling_factor)
        
        # Solar generation: higher in sunny months (Feb-May)
        solar_factor = 1.4 if i in [1, 2, 3, 4] else (0.8 if i in [6, 7] else 1.1)
        solar_kwh = int(np.random.uniform(18000, 24000) * solar_factor)
        
        # Diesel generator (backup power spikes during grid load shedding in summer)
        dg_liters = int(np.random.uniform(800, 1400) * (1.5 if i in [4, 5, 6] else 1.0))
        
        # Campus fleet (diesel shuttles, petrol utility cars, CNG vans)
        diesel_fleet_l = int(np.random.uniform(2200, 2800))
        petrol_fleet_l = int(np.random.uniform(900, 1300))
        cng_fleet_kg = int(np.random.uniform(350, 550))
        
        # Canteen LPG
        lpg_kg = int(np.random.uniform(450, 650))
        
        # Scope 3 activities (commute drops in festive/vacation months e.g. Dec, May)
        commute_factor = 0.75 if i in [4, 11] else 1.0
        commute_pkm = int(np.random.uniform(140000, 180000) * commute_factor)
        flight_pkm = int(np.random.uniform(15000, 45000))
        solid_waste = int(np.random.uniform(3200, 4800))
        paper_kg = int(np.random.uniform(350, 600))
        
        data.append({
            "Month": month,
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
        
    return pd.DataFrame(data)


def ensure_sample_data_file(target_path: Optional[str] = None) -> str:
    """
    Ensures that the sample dataset CSV is written to disk for easy loading.
    """
    if target_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        target_path = os.path.join(base_dir, "data", "sample_campus_emissions.csv")
        
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    if not os.path.exists(target_path):
        df = generate_campus_sample_data()
        df.to_csv(target_path, index=False)
        
    return target_path
