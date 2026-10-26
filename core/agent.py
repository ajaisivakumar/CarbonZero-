"""
CarbonZero AI Agent: Autonomous Carbon Auditor & Decarbonization Copilot.
Features tool calling, emission diagnostics, EV scenario simulation, green skills matching,
and executive ESG report generation.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from core.calculator import get_emission_summary, process_emissions_dataframe
from core.simulator import simulate_ev_transition


# Curated Green Skills & Certifications Database
GREEN_SKILLS_DATABASE = {
    "ev": {
        "domain": "Electric Mobility & EV Fleet Engineering",
        "key_skills": [
            "Battery Management Systems (BMS) Calibration",
            "EV Charging Infrastructure Planning (OCPP, Level 2 / DC Fast)",
            "High Voltage Safety (SAE J1772, ISO 6469)",
            "Fleet Telematics & Range Optimization Algorithms",
            "Lithium-ion Battery Recycling & Second-Life Valuation"
        ],
        "recommended_certifications": [
            "Certified EV Powertrain & Battery Systems Engineer (SAE International)",
            "EV Infrastructure & Charging Station Management (TERI / IEEE)",
            "Automotive Functional Safety Professional (ISO 26262)"
        ],
        "target_roles": ["EV Fleet Operations Manager", "BMS Systems Engineer", "Charging Infra Architect"]
    },
    "renewable_energy": {
        "domain": "Renewable Energy & Solar Microgrids",
        "key_skills": [
            "Rooftop Solar PV Sizing & Shading Analysis (PVSyst, Helioscope)",
            "Solar Microgrid Inverter & BESS (Battery Storage) Integration",
            "Net Metering & Power Purchase Agreement (PPA) Structuring",
            "Smart Grid Peak-Shaving & Demand Response Dispatch"
        ],
        "recommended_certifications": [
            "NABCEP PV Installation Professional / Associate",
            "Certified Energy Auditor (CEA) - Bureau of Energy Efficiency (BEE)",
            "Microgrid Design & Distributed Energy Resources Specialist (IEEE)"
        ],
        "target_roles": ["Solar Microgrid Engineer", "Distributed Energy Planner", "Clean Energy Analyst"]
    },
    "esg_auditing": {
        "domain": "Corporate ESG Auditing & Carbon Accounting",
        "key_skills": [
            "GHG Protocol Corporate Standard (Scope 1, 2, 3 Accounting)",
            "Life Cycle Assessment (LCA - ISO 14040/44) & Carbon Neutrality Verification",
            "BRSR (Business Responsibility & Sustainability Reporting) Framework",
            "Science Based Targets initiative (SBTi) Net-Zero Modeling",
            "TCFD Climate Risk Scenario Analysis"
        ],
        "recommended_certifications": [
            "GRI Certified Sustainability Professional (Global Reporting Initiative)",
            "ISO 14064 Carbon Footprint Lead Auditor",
            "GARP Sustainability and Climate Risk (SCR) Certification"
        ],
        "target_roles": ["Sustainability Auditor", "Carbon Accounting Officer", "ESG Reporting Manager"]
    },
    "energy_efficiency": {
        "domain": "Facility Energy Efficiency & Green Buildings",
        "key_skills": [
            "HVAC Variable Speed Drive (VSD) Optimization & Chiller Plant Tuning",
            "Building Management System (BMS/IoT) Automation",
            "ASHRAE Level II Facility Energy Auditing",
            "Green Building Ratings (LEED AP / GRIHA Evaluator)"
        ],
        "recommended_certifications": [
            "Certified Energy Manager (CEM) - AEE",
            "LEED Accredited Professional (Operations + Maintenance)",
            "GRIHA Certified Professional"
        ],
        "target_roles": ["Facility Energy Manager", "Smart Building IoT Specialist", "Energy Efficiency Consultant"]
    }
}


class CarbonZeroAgent:
    """
    Intelligent agent equipped with carbon accounting and EV simulation tools.
    """
    
    def __init__(self, data_df: Optional[pd.DataFrame] = None, custom_grid_factor: Optional[float] = None):
        self.data_df = data_df
        self.custom_grid_factor = custom_grid_factor
        self.processed_df = None
        self.summary = None
        
        if self.data_df is not None:
            self._update_data(self.data_df, self.custom_grid_factor)
            
    def _update_data(self, data_df: pd.DataFrame, custom_grid_factor: Optional[float] = None):
        self.data_df = data_df
        self.custom_grid_factor = custom_grid_factor
        self.processed_df = process_emissions_dataframe(data_df, custom_grid_factor)
        self.summary = get_emission_summary(self.processed_df)
        
    # --- TOOL 1: Emission Diagnostics Tool ---
    def tool_diagnose_emissions(self) -> Dict[str, Any]:
        """Analyzes carbon emissions, breakdown by scope, and identifies top polluters."""
        if self.summary is None:
            return {"error": "No dataset loaded. Please load or generate campus emission data first."}
            
        top_hotspot = self.summary["hotspots"][0] if self.summary["hotspots"] else {"source": "N/A", "emissions_tco2e": 0}
        
        return {
            "total_emissions_tco2e": self.summary["grand_total_tco2e"],
            "scope_1_pct": self.summary["scope_1_share_pct"],
            "scope_2_pct": self.summary["scope_2_share_pct"],
            "scope_3_pct": self.summary["scope_3_share_pct"],
            "fleet_emissions_tco2e": self.summary["fleet_emissions_tco2e"],
            "top_emission_hotspot": top_hotspot,
            "hotspots": self.summary["hotspots"][:5]
        }
        
    # --- TOOL 2: EV Fleet Transition Simulator Tool ---
    def tool_simulate_ev(self, electrification_pct: float = 50.0, solar_pct: float = 40.0, total_vehicles: int = 30) -> Dict[str, Any]:
        """Runs the EV fleet transition model and returns carbon abatement and financial ROI."""
        return simulate_ev_transition(
            total_ice_vehicles=total_vehicles,
            electrification_pct=electrification_pct,
            solar_charging_share_pct=solar_pct
        )
        
    # --- TOOL 3: Decarbonization Action Recommender Tool ---
    def tool_recommend_actions(self) -> List[Dict[str, Any]]:
        """Generates a prioritized, high-ROI decarbonization roadmap based on current audit hotspots."""
        if self.summary is None:
            return []
            
        actions = []
        
        # Action 1: Fleet Electrification
        if self.summary["fleet_emissions_tco2e"] > 0:
            actions.append({
                "priority": "HIGH",
                "initiative": "Phase-in EV Campus Shuttles & Pool Cars (60% Fleet)",
                "category": "Clean Mobility",
                "estimated_co2_reduction_tco2e": round(self.summary["fleet_emissions_tco2e"] * 0.65, 1),
                "capex_requirement": "Medium (Net of FAME Subsidies)",
                "payback_years": "3.5 - 4.5 Years",
                "action_steps": [
                    "Replace high-mileage diesel shuttles with 9-12m electric passenger vans.",
                    "Install 4x Level 2 dual-gun AC smart chargers in campus depot.",
                    "Integrate smart scheduled charging during non-peak hours."
                ]
            })
            
        # Action 2: Solar Rooftop Expansion
        grid_emissions = self.summary["breakdown"].get("Scope 2 - Grid Electricity", 0)
        if grid_emissions > 50:
            actions.append({
                "priority": "HIGH",
                "initiative": "Rooftop Solar PV Expansion with Net Metering (150 kWp)",
                "category": "Renewable Energy",
                "estimated_co2_reduction_tco2e": round(grid_emissions * 0.35, 1),
                "capex_requirement": "Medium-High",
                "payback_years": "4.0 Years",
                "action_steps": [
                    "Conduct solar irradiation and shading audit across academic & administrative roofs.",
                    "Deploy 150 kWp bifacial monocrystalline solar panels with grid-tie inverters.",
                    "Pair directly with daytime EV charging stations to provide zero-emission charging."
                ]
            })
            
        # Action 3: Commuter Green Mobility
        commute_emissions = self.summary["breakdown"].get("Scope 3 - Employee Commute", 0)
        if commute_emissions > 0:
            actions.append({
                "priority": "MEDIUM",
                "initiative": "Green Commute Program & Subsidized Electric 2-Wheeler Charging",
                "category": "Scope 3 Abatement",
                "estimated_co2_reduction_tco2e": round(commute_emissions * 0.25, 1),
                "capex_requirement": "Low",
                "payback_years": "Immediate (Operational Benefit)",
                "action_steps": [
                    "Launch campus carpooling app and dedicated EV parking bays.",
                    "Install free 15A solar-powered charging points for student/staff e-scooters and e-bikes.",
                    "Introduce 1-2 days/week hybrid telecommuting policy for eligible roles."
                ]
            })
            
        # Action 4: Diesel Generator Hybridization
        dg_emissions = self.summary["breakdown"].get("Scope 1 - Diesel Generators", 0)
        if dg_emissions > 10:
            actions.append({
                "priority": "MEDIUM",
                "initiative": "Battery Energy Storage System (BESS) for DG Hybridization",
                "category": "Grid Resilience",
                "estimated_co2_reduction_tco2e": round(dg_emissions * 0.50, 1),
                "capex_requirement": "Medium",
                "payback_years": "3.8 Years",
                "action_steps": [
                    "Deploy 100 kWh Lithium Iron Phosphate (LFP) BESS to handle transient power dips.",
                    "Reduce diesel generator run hours by 60% via instant solar/battery cutover."
                ]
            })
            
        return actions
        
    # --- TOOL 4: Green Skills & Upskilling Matcher Tool ---
    def tool_recommend_green_skills(self, focus_area: str = "all") -> Dict[str, Any]:
        """Matches organizational roles to in-demand green skills and professional credentials."""
        focus_lower = focus_area.lower()
        if "ev" in focus_lower or "electric" in focus_lower or "mobility" in focus_lower or "fleet" in focus_lower:
            return {"domain": "EV", "data": GREEN_SKILLS_DATABASE["ev"]}
        elif "solar" in focus_lower or "energy" in focus_lower or "grid" in focus_lower or "renew" in focus_lower:
            return {"domain": "Renewable Energy", "data": GREEN_SKILLS_DATABASE["renewable_energy"]}
        elif "esg" in focus_lower or "audit" in focus_lower or "carbon" in focus_lower or "report" in focus_lower:
            return {"domain": "ESG & Carbon Auditing", "data": GREEN_SKILLS_DATABASE["esg_auditing"]}
        elif "hvac" in focus_lower or "building" in focus_lower or "facility" in focus_lower:
            return {"domain": "Facility Efficiency", "data": GREEN_SKILLS_DATABASE["energy_efficiency"]}
        else:
            return {"domain": "All Green Skill Tracks", "database": GREEN_SKILLS_DATABASE}

    # --- Agent Reasoning & Response Synthesizer ---
    def answer_query(self, user_query: str) -> str:
        """
        Processes user query, executes the appropriate tool(s), and returns a structured response.
        """
        q = user_query.lower()
        
        # 1. EV Simulation Intent
        if any(term in q for term in ["ev", "electric vehicle", "fleet", "simulate", "switch to ev", "charging"]):
            # Extract percentage if specified
            import re
            pct_matches = re.findall(r"(\d+)\s*%", q)
            pct = float(pct_matches[0]) if pct_matches else 60.0
            
            sim_res = self.tool_simulate_ev(electrification_pct=pct, solar_pct=40.0)
            return (
                f"### ⚡ EV Fleet Transition Simulation ({pct}% Electrification)\n\n"
                f"I simulated converting **{pct}%** ({sim_res['ev_count']} out of {sim_res['total_ice_vehicles']} vehicles) "
                f"of your campus fleet to Electric Vehicles:\n\n"
                f"- **🌱 Carbon Avoided:** **{sim_res['annual_co2_saved_tco2e']} tonnes $CO_2e$/year** "
                f"(*{sim_res['co2_reduction_pct']}% reduction in fleet emissions*).\n"
                f"- **⛽ Fuel Saved:** **{sim_res['annual_fuel_saved_liters']:,.0f} Liters** "
                f"(Saving **₹{sim_res['annual_fuel_cost_saved']:,.2f}** annually).\n"
                f"- **⚡ Electricity Needed:** **{sim_res['annual_ev_electricity_kwh']:,.0f} kWh/year** "
                f"(Charging Cost: ₹{sim_res['annual_charging_cost']:,.2f}).\n"
                f"- **🛠️ Maintenance Savings:** **₹{sim_res['annual_maintenance_savings']:,.2f}/year**.\n"
                f"- **💰 Net Annual Savings:** **₹{sim_res['net_annual_savings']:,.2f}**.\n"
                f"- **🔌 Charging Infra Required:** **{sim_res['ac_chargers_needed']}x AC Level-2 Chargers** "
                f"and **{sim_res['dc_chargers_needed']}x DC Fast Chargers**.\n"
                f"- **⏱️ Estimated Financial Payback:** **{sim_res['payback_years']} years** "
                f"(8-Year ROI: **{sim_res['roi_8yr_pct']}%**).\n"
                f"- **☀️ Solar Microgrid Synergy:** Pairing 40% charging with rooftop solar prevents an extra "
                f"**{sim_res['solar_carbon_benefit_tco2e']} tonnes $CO_2e$** compared to pure coal-grid charging!"
            )
            
        # 2. Green Skills Intent
        elif any(term in q for term in ["skill", "career", "training", "certif", "upskill", "learn", "course", "role"]):
            skills_info = self.tool_recommend_green_skills(q)
            if "data" in skills_info:
                track = skills_info["data"]
                return (
                    f"### 🎓 Green Skills & Certification Roadmap: {track['domain']}\n\n"
                    f"To prepare your technical workforce and students for the clean transition, here are high-impact competencies:\n\n"
                    f"**Core In-Demand Skills:**\n" +
                    "\n".join([f"- {skill}" for skill in track["key_skills"]]) +
                    f"\n\n**Industry-Recognized Certifications:**\n" +
                    "\n".join([f"- 📜 {cert}" for cert in track["recommended_certifications"]]) +
                    f"\n\n**Emerging Job Roles:** " + ", ".join(track["target_roles"])
                )
            else:
                return (
                    f"### 🎓 Green Skills Matrix (Edunet Specialization Tracks)\n\n"
                    f"The green economy requires specialized cross-disciplinary skills across 4 key pillars:\n\n"
                    f"1. **⚡ EV & E-Mobility:** Battery Management Systems (BMS), Charging Infrastructure (OCPP), High-Voltage Safety.\n"
                    f"2. **☀️ Clean Energy:** Rooftop Solar PV Engineering (PVSyst), Microgrid Inverters, Battery Energy Storage (BESS).\n"
                    f"3. **📊 ESG & Carbon Auditing:** GHG Protocol (Scope 1/2/3), ISO 14064, BRSR Sustainability Reporting.\n"
                    f"4. **🏢 Smart Facilities:** HVAC Variable Drives, IoT Building Automation, LEED/GRIHA green ratings.\n\n"
                    f"*Ask me about any specific track (e.g. 'What EV certifications should our engineers get?') for deep-dive recommendations!*"
                )
                
        # 3. Action Plan / Decarbonization Roadmap
        elif any(term in q for term in ["action", "reduce", "plan", "roadmap", "strategy", "mitigat", "decarboniz"]):
            actions = self.tool_recommend_actions()
            if not actions:
                return "Please load or generate an emission dataset first to calculate actionable recommendations."
                
            resp = ["### 🚀 Prioritized Campus Decarbonization Action Plan\n"]
            for act in actions:
                resp.append(
                    f"#### [{act['priority']}] {act['initiative']} ({act['category']})\n"
                    f"- **Estimated Carbon Abatement:** ~{act['estimated_co2_reduction_tco2e']} $tCO_2e$/year\n"
                    f"- **CapEx & Payback:** {act['capex_requirement']} | Payback: **{act['payback_years']}**\n"
                    f"- **Actionable Milestones:**\n  " +
                    "\n  ".join([f"• {step}" for step in act["action_steps"]]) + "\n"
                )
            return "\n".join(resp)
            
        # 4. Emission Diagnostics & Hotspots (Default / Specific query)
        else:
            diag = self.tool_diagnose_emissions()
            if "error" in diag:
                return diag["error"]
                
            hotspots_str = "\n".join([
                f"- **{h['source']}**: {h['emissions_tco2e']} $tCO_2e$ ({h['share_pct']}% of total footprint)"
                for h in diag["hotspots"]
            ])
            
            return (
                f"### 📊 Carbon Audit Diagnostic Summary\n\n"
                f"- **Total Annual Carbon Footprint:** **{diag['total_emissions_tco2e']} metric tonnes $CO_2e$**\n"
                f"- **Scope Breakdown:**\n"
                f"  - **Scope 1 (Direct Fuel & Fleet):** {diag['scope_1_pct']}%\n"
                f"  - **Scope 2 (Purchased Electricity):** {diag['scope_2_pct']}%\n"
                f"  - **Scope 3 (Commute, Flights, Waste):** {diag['scope_3_pct']}%\n\n"
                f"- **🔥 Top Emission Hotspots:**\n{hotspots_str}\n\n"
                f"- **🚗 Vehicle Fleet Footprint:** **{diag['fleet_emissions_tco2e']} $tCO_2e$**.\n\n"
                f"*💡 Tip: Ask me to **'Simulate EV transition for 70% of fleet'** or **'Recommend decarbonization roadmap'** to explore abatement strategies!*"
            )
