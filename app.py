"""
CarbonZero: Enterprise & Campus Carbon Footprint Auditor & EV Action Agent.
An AI-powered ESG intelligence application for sustainability auditing, EV fleet
simulation, and green workforce skills development.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from core.calculator import (
    process_emissions_dataframe,
    get_emission_summary,
    EMISSION_FACTORS
)
from core.simulator import simulate_ev_transition
from core.agent import CarbonZeroAgent
from core.data_generator import generate_campus_sample_data, ensure_sample_data_file
from core.llm_client import call_llm_api

# --- Page Configuration ---
st.set_page_config(
    page_title="CarbonZero | AI Carbon Auditor & EV Agent",
    page_icon="ðŸŒ±",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for polished, modern look
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1b5e20;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #455a64;
        margin-bottom: 20px;
    }
    .kpi-card {
        background-color: #f1f8e9;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #2e7d32;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .kpi-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        color: #558b2f;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1b5e20;
    }
</style>
""", unsafe_allow_html=True)


# --- Ensure Sample Data Exists & Initialize State ---
ensure_sample_data_file()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": (
                "ðŸ‘‹ Hello! I am **CarbonZero**, your AI Sustainability & EV Transition Copilot. "
                "I can audit your campus/enterprise emissions (Scope 1, 2, 3), simulate EV fleet conversion scenarios, "
                "and recommend green workforce upskilling tracks.\n\n"
                "Try asking me:\n"
                "- *'What are our biggest emission hotspots?'*\n"
                "- *'Simulate converting 75% of our campus fleet to EVs with solar charging'*\n"
                "- *'What green skills and certifications should our engineering team learn?'*"
            )
        }
    ]

if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "api_provider" not in st.session_state:
    st.session_state.api_provider = "Gemini"


# --- Sidebar Navigation & Controls ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1508873696983-2df5293cb395?auto=format&fit=crop&w=400&q=80", width='stretch')
    st.title("ðŸŒ± CarbonZero")
    st.caption("AI Carbon Footprint Auditor & EV Copilot")
    st.markdown("---")
    
    st.subheader("ðŸ“ Data Source")
    data_source = st.radio(
        "Choose Emissions Telemetry:",
        ["ðŸ« Preloaded Campus Dataset", "ðŸ“¤ Upload Custom CSV"],
        index=0
    )
    
    custom_df = None
    if data_source == "ðŸ“¤ Upload Custom CSV":
        uploaded_file = st.file_uploader("Upload CSV (monthly energy & fleet logs)", type=["csv"])
        if uploaded_file is not None:
            try:
                custom_df = pd.read_csv(uploaded_file)
                st.success("Custom data loaded successfully!")
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
    
    st.markdown("---")
    st.subheader("âš™ï¸ Regional Grid Parameters")
    grid_emission_factor = st.slider(
        "Grid Emission Factor (kg COâ‚‚e/kWh)",
        min_value=0.200,
        max_value=0.950,
        value=0.713,
        step=0.010,
        help="0.713 is CEA India average. EU avg is ~0.250, US avg is ~0.380."
    )
    
    st.markdown("---")
    st.markdown("### ðŸ† Edunet Project Showcase")
    st.info(
        "**Theme:** Green Skills & EV Innovation\n\n"
        "**Standards:** GHG Protocol Corporate Standard (Scope 1, 2, 3) & ISO 14064."
    )

    # ------------------------------------------------------------------ #
    # API KEY PANEL
    # ------------------------------------------------------------------ #
    st.markdown("---")
    st.subheader("ðŸ”‘ AI Chatbot API Key")
    st.caption(
        "Provide your own API key to power the CarbonZero chatbot with a real LLM. "
        "Without a key, the built-in offline engine is used."
    )

    api_provider_choice = st.selectbox(
        "Select AI Provider",
        ["Gemini", "Groq", "OpenAI"],
        index=["Gemini", "Groq", "OpenAI"].index(st.session_state.api_provider)
    )
    st.session_state.api_provider = api_provider_choice

    api_key_input = st.text_input(
        f"{api_provider_choice} API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder=f"Paste your {api_provider_choice} API key here..."
    )

    if st.button("âœ… Save & Activate Key"):
        st.session_state.api_key = api_key_input.strip()
        if st.session_state.api_key:
            st.success(f"âœ… {api_provider_choice} API key saved! The chatbot will now use this key.")
        else:
            st.warning("No key entered. The built-in offline engine will be used.")

    if st.session_state.api_key:
        st.markdown(
            f"<span style='color:#2e7d32;font-size:0.82rem;'>ðŸŸ¢ <b>{st.session_state.api_provider}</b> key active</span>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<span style='color:#888;font-size:0.82rem;'>âš« No key â€” using built-in offline engine</span>",
            unsafe_allow_html=True
        )


# --- Load & Process Data ---
if custom_df is not None:
    raw_df = custom_df
else:
    raw_df = generate_campus_sample_data()

processed_df = process_emissions_dataframe(raw_df, custom_grid_factor=grid_emission_factor)
summary = get_emission_summary(processed_df)

# Initialize AI Agent with current processed data
agent = CarbonZeroAgent(raw_df, custom_grid_factor=grid_emission_factor)


# --- Main Header ---
st.markdown('<div class="main-header">ðŸŒ± CarbonZero: Autonomous Sustainability & EV Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">GHG Protocol Scope 1-2-3 Carbon Accounting â€¢ EV Fleet Electrification Simulator â€¢ Green Skills Advisor</div>',
    unsafe_allow_html=True
)

# --- Top Navigation Tabs ---
tab_dash, tab_sim, tab_chat, tab_report = st.tabs([
    "ðŸ“Š Executive Dashboard",
    "âš¡ EV Fleet & Solar Simulator",
    "ðŸ¤– CarbonZero AI Agent",
    "ðŸ“‘ Sustainability Audit Report"
])


# ==============================================================================
# TAB 1: EXECUTIVE CARBON DASHBOARD
# ==============================================================================
with tab_dash:
    st.markdown("### ðŸ›ï¸ Campus Annual Carbon Footprint Overview")
    
    # 4 Key Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Emissions</div>
            <div class="kpi-value">{summary['grand_total_tco2e']:,.1f} <span style="font-size:1rem;color:#558b2f;">tCOâ‚‚e</span></div>
            <span style="font-size:0.8rem;color:#666;">Annual Scope 1 + 2 + 3</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color:#d32f2f;">
            <div class="kpi-title" style="color:#d32f2f;">Scope 1 (Direct)</div>
            <div class="kpi-value" style="color:#b71c1c;">{summary['scope_1_tco2e']:,.1f} <span style="font-size:1rem;">tCOâ‚‚e</span></div>
            <span style="font-size:0.8rem;color:#666;"><b>{summary['scope_1_share_pct']}%</b> of total footprint</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color:#1976d2;">
            <div class="kpi-title" style="color:#1976d2;">Scope 2 (Electricity)</div>
            <div class="kpi-value" style="color:#0d47a1;">{summary['scope_2_tco2e']:,.1f} <span style="font-size:1rem;">tCOâ‚‚e</span></div>
            <span style="font-size:0.8rem;color:#666;"><b>{summary['scope_2_share_pct']}%</b> of total footprint</span>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color:#f57c00;">
            <div class="kpi-title" style="color:#f57c00;">Scope 3 (Value Chain)</div>
            <div class="kpi-value" style="color:#e65100;">{summary['scope_3_tco2e']:,.1f} <span style="font-size:1rem;">tCOâ‚‚e</span></div>
            <span style="font-size:0.8rem;color:#666;"><b>{summary['scope_3_share_pct']}%</b> of total footprint</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Visual Row 1: Donut Chart & Stacked Monthly Timeline
    col_g1, col_g2 = st.columns([1, 1.6])
    
    with col_g1:
        st.markdown("#### ðŸ© Emissions by Scope")
        scope_fig = px.pie(
            values=[summary['scope_1_tco2e'], summary['scope_2_tco2e'], summary['scope_3_tco2e']],
            names=["Scope 1 (Direct)", "Scope 2 (Purchased Electricity)", "Scope 3 (Commute/Travel/Waste)"],
            hole=0.55,
            color_discrete_sequence=["#e53935", "#1e88e5", "#fb8c00"]
        )
        scope_fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320, legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(scope_fig, width='stretch')
        
    with col_g2:
        st.markdown("#### ðŸ“ˆ Monthly Emissions Trajectory (tCOâ‚‚e)")
        monthly_fig = go.Figure()
        monthly_fig.add_trace(go.Bar(
            x=processed_df["Month"], y=processed_df["Scope_1_Total"],
            name="Scope 1", marker_color="#e53935"
        ))
        monthly_fig.add_trace(go.Bar(
            x=processed_df["Month"], y=processed_df["Scope_2_Total"],
            name="Scope 2", marker_color="#1e88e5"
        ))
        monthly_fig.add_trace(go.Bar(
            x=processed_df["Month"], y=processed_df["Scope_3_Total"],
            name="Scope 3", marker_color="#fb8c00"
        ))
        monthly_fig.update_layout(
            barmode="stack",
            margin=dict(t=10, b=10, l=10, r=10),
            height=320,
            xaxis_title="",
            yaxis_title="Emissions (tCOâ‚‚e)",
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(monthly_fig, width='stretch')

    # Visual Row 2: Top Emission Hotspots & Clean Solar Ratio
    col_h1, col_h2 = st.columns([1.5, 1])
    
    with col_h1:
        st.markdown("#### ðŸ”¥ Ranked Emission Hotspots")
        hotspots_df = pd.DataFrame(summary["hotspots"]).head(6)
        hotspot_bar = px.bar(
            hotspots_df,
            x="emissions_tco2e",
            y="source",
            orientation="h",
            color="emissions_tco2e",
            color_continuous_scale="Reds",
            text="emissions_tco2e"
        )
        hotspot_bar.update_layout(
            yaxis=dict(autorange="reversed"),
            height=280,
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis_title="tCOâ‚‚e",
            yaxis_title="",
            coloraxis_showscale=False
        )
        st.plotly_chart(hotspot_bar, width='stretch')
        
    with col_h2:
        st.markdown("#### â˜€ï¸ Clean Energy Share (Solar vs Grid)")
        total_grid_kwh = raw_df["grid_electricity_kwh"].sum()
        total_solar_kwh = raw_df["solar_electricity_kwh"].sum()
        total_power = total_grid_kwh + total_solar_kwh
        solar_pct = (total_solar_kwh / total_power * 100) if total_power > 0 else 0
        
        st.metric("Total Solar Generation", f"{total_solar_kwh:,.0f} kWh", f"{solar_pct:.1f}% of total power")
        st.metric("Grid Electricity Consumption", f"{total_grid_kwh:,.0f} kWh")
        st.metric("Fleet Fuel Emissions", f"{summary['fleet_emissions_tco2e']} tCOâ‚‚e", f"{summary['fleet_share_pct']}% of total")


# ==============================================================================
# TAB 2: EV FLEET & SOLAR SCENARIO SIMULATOR
# ==============================================================================
with tab_sim:
    st.markdown("### âš¡ Interactive EV Fleet Transition & Microgrid Simulator")
    st.markdown(
        "Evaluate the decarbonization impact, fuel savings, charging equipment needs, and financial payback "
        "of transitioning campus ICE vehicles to electric fleets."
    )
    
    col_ctrl, col_results = st.columns([1, 1.6])
    
    with col_ctrl:
        st.markdown("#### ðŸŽ›ï¸ Simulation Controls")
        sim_total_vehicles = st.number_input("Total ICE Fleet Vehicles", min_value=5, max_value=200, value=30, step=5)
        sim_pct = st.slider("Fleet Electrification Target (%)", min_value=0, max_value=100, value=60, step=10)
        sim_annual_km = st.number_input("Average Annual km / Vehicle", min_value=5000, max_value=80000, value=25000, step=1000)
        sim_fuel_price = st.number_input("Fuel Price (â‚¹/Liter or currency)", min_value=50.0, max_value=200.0, value=96.0, step=1.0)
        sim_solar_share = st.slider("Solar PV Powered Charging (%)", min_value=0, max_value=100, value=40, step=10)
        sim_elec_cost = st.number_input("Commercial Grid Tariff (â‚¹/kWh)", min_value=3.0, max_value=20.0, value=7.5, step=0.5)
        
    # Execute Simulation
    sim_data = simulate_ev_transition(
        total_ice_vehicles=sim_total_vehicles,
        electrification_pct=float(sim_pct),
        avg_annual_km_per_vehicle=float(sim_annual_km),
        current_fuel_price_per_liter=float(sim_fuel_price),
        electricity_cost_per_kwh=float(sim_elec_cost),
        solar_charging_share_pct=float(sim_solar_share),
        grid_emission_factor_kg_per_kwh=grid_emission_factor
    )
    
    with col_results:
        st.markdown(f"#### ðŸŽ¯ Impact for {sim_data['ev_count']} Electric Vehicles ({sim_pct}% Fleet)")
        
        # Metric Cards
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.metric("ðŸŒ± COâ‚‚e Saved / Year", f"{sim_data['annual_co2_saved_tco2e']} tCOâ‚‚e", f"-{sim_data['co2_reduction_pct']}% fleet COâ‚‚")
        with sc2:
            st.metric("ðŸ’° Net Annual Savings", f"â‚¹{sim_data['net_annual_savings']:,.0f}", "Fuel + Maintenance")
        with sc3:
            st.metric("â±ï¸ Payback Period", f"{sim_data['payback_years']} Years", f"8-Yr ROI: {sim_data['roi_8yr_pct']}%")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Financial Comparison Chart
        st.markdown("##### ðŸ’µ Annual Operating Cost Comparison (â‚¹)")
        # Baseline ICE vs EV
        baseline_cost = sim_data['annual_fuel_cost_saved'] + (sim_data['ev_count'] * 35000)
        ev_opex = sim_data['annual_charging_cost'] + (sim_data['ev_count'] * 18000)
        
        fig_cost = go.Figure(data=[
            go.Bar(name='Baseline (ICE Fuel & Maintenance)', x=['Annual Operating Expense'], y=[baseline_cost], marker_color='#ef5350'),
            go.Bar(name='EV Fleet (Charging & Maintenance)', x=['Annual Operating Expense'], y=[ev_opex], marker_color='#66bb6a')
        ])
        fig_cost.update_layout(
            barmode='group',
            height=260,
            margin=dict(t=10, b=10, l=10, r=10),
            yaxis_title="Annual OpEx (â‚¹)"
        )
        st.plotly_chart(fig_cost, width='stretch')
        
        # Infra & Equipment specs
        st.markdown("##### ðŸ”Œ Required EV Charging Infrastructure")
        st.markdown(
            f"- **Level 2 Smart AC Chargers (7.4 - 22 kW):** **{sim_data['ac_chargers_needed']} units** (overnight depot charging)\n"
            f"- **DC Fast Chargers (30 - 60 kW):** **{sim_data['dc_chargers_needed']} units** (rapid daytime turnaround)\n"
            f"- **Total Infrastructure CapEx:** â‚¹{sim_data['infra_capex']:,.2f}\n"
            f"- **â˜€ï¸ Solar Microgrid Synergy:** Solar charging avoids an additional **{sim_data['solar_carbon_benefit_tco2e']} tCOâ‚‚e** every year!"
        )


# ==============================================================================
# TAB 3: CARBONZERO AI AGENT
# ==============================================================================
with tab_chat:
    st.markdown("### ðŸ¤– Autonomous CarbonZero Copilot")
    st.markdown("Ask the AI agent anything about emission diagnostics, EV transition plans, or green workforce skills.")
    
    # Quick prompt buttons
    st.markdown("**âš¡ Quick Action Prompts:**")
    qb1, qb2, qb3, qb4 = st.columns(4)
    preset_query = None
    if qb1.button("ðŸ”¥ Diagnose Hotspots"):
        preset_query = "What are our top emission hotspots and diagnostic summary?"
    if qb2.button("ðŸš— Simulate 75% EV Fleet"):
        preset_query = "Simulate converting 75% of our fleet to electric vehicles with solar charging"
    if qb3.button("ðŸ“‹ Decarbonization Plan"):
        preset_query = "Recommend prioritized decarbonization roadmap for our campus"
    if qb4.button("ðŸŽ“ EV & Green Skills"):
        preset_query = "What EV and clean energy green skills and certifications should our team learn?"

    st.markdown("---")
    
    # Display message history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Handle user message
    user_input = st.chat_input("Ask CarbonZero (e.g., 'What is our Scope 2 emission?', 'Simulate 50% EV conversion')...")
    
    active_prompt = preset_query if preset_query else user_input
    
    if active_prompt:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": active_prompt})
        with st.chat_message("user"):
            st.markdown(active_prompt)

        # ------------------------------------------------------------------ #
        # RESPONSE LOGIC: Use real LLM if API key provided, else offline agent
        # ------------------------------------------------------------------ #
        with st.chat_message("assistant"):
            with st.spinner("CarbonZero Agent analyzing telemetry and executing tools..."):

                user_api_key = st.session_state.get("api_key", "").strip()
                user_provider = st.session_state.get("api_provider", "Gemini")

                if user_api_key:
                    # Build a rich system prompt embedding the current emissions context
                    system_prompt = (
                        "You are CarbonZero, an expert AI sustainability and electric vehicle (EV) agent. "
                        "You help campuses, enterprises, and institutions reduce their carbon footprint. "
                        "You are an authority on GHG Protocol (Scope 1, 2, 3), EV fleet transitions, "
                        "solar microgrids, green skills, ESG auditing, and decarbonization roadmaps.\n\n"
                        f"Current campus emissions data context:\n"
                        f"- Total Annual Footprint: {summary['grand_total_tco2e']} tCO2e\n"
                        f"- Scope 1 (Direct): {summary['scope_1_tco2e']} tCO2e ({summary['scope_1_share_pct']}%)\n"
                        f"- Scope 2 (Electricity): {summary['scope_2_tco2e']} tCO2e ({summary['scope_2_share_pct']}%)\n"
                        f"- Scope 3 (Commute/Travel/Waste): {summary['scope_3_tco2e']} tCO2e ({summary['scope_3_share_pct']}%)\n"
                        f"- Top emission source: {summary['hotspots'][0]['source']} "
                        f"({summary['hotspots'][0]['emissions_tco2e']} tCO2e, {summary['hotspots'][0]['share_pct']}%)\n"
                        f"- Fleet emissions: {summary['fleet_emissions_tco2e']} tCO2e "
                        f"({summary['fleet_share_pct']}% of total)\n\n"
                        "Answer the user's question in a clear, concise, and professional manner. "
                        "Use markdown formatting where helpful (bullet points, bold key figures). "
                        "Always relate your answer back to the sustainability or green skills context."
                    )

                    success, response_text = call_llm_api(
                        provider=user_provider,
                        api_key=user_api_key,
                        system_prompt=system_prompt,
                        user_message=active_prompt
                    )

                    if not success:
                        # Show the API error notification prominently
                        st.error(response_text)
                        response_text = response_text  # store error in history too
                    else:
                        st.markdown(response_text)
                else:
                    # Offline built-in agent
                    response_text = agent.answer_query(active_prompt)
                    st.markdown(response_text)

        st.session_state.chat_history.append({"role": "assistant", "content": response_text})


# ==============================================================================
# TAB 4: SUSTAINABILITY AUDIT REPORT
# ==============================================================================
with tab_report:
    st.markdown("### ðŸ“‘ Official Campus Sustainability & GHG Audit Report")
    st.markdown("Standardized executive report aligned with **GHG Protocol** & **ISO 14064** specifications.")
    
    report_md = f"""# Executive GHG Emissions & Decarbonization Audit Report
**Organization / Facility:** Academic & Technology Campus  
**Reporting Period:** 12-Month Annual Cycle  
**Audit Standard:** GHG Protocol Corporate Standard (Scope 1, Scope 2, Scope 3)  
**Date Generated:** {datetime.now().strftime("%Y-%m-%d")}  

---

## 1. Executive Summary
During the 12-month reporting cycle, the facility generated an aggregate footprint of **{summary['grand_total_tco2e']} metric tonnes of COâ‚‚ equivalent (tCOâ‚‚e)**.

| Scope Classification | Emissions (tCOâ‚‚e) | Share of Total (%) | Primary Activity Drivers |
| :--- | :---: | :---: | :--- |
| **Scope 1 (Direct)** | {summary['scope_1_tco2e']} | {summary['scope_1_share_pct']}% | Diesel Generators, Internal Combustion Fleet, Canteen LPG |
| **Scope 2 (Indirect)** | {summary['scope_2_tco2e']} | {summary['scope_2_share_pct']}% | Purchased Grid Electricity ({grid_emission_factor} kg COâ‚‚e/kWh) |
| **Scope 3 (Value Chain)** | {summary['scope_3_tco2e']} | {summary['scope_3_share_pct']}% | Commuter Passenger Miles, Business Travel, Solid Waste |
| **TOTAL** | **{summary['grand_total_tco2e']}** | **100.0%** | |

---

## 2. Top Identified Hotspots
1. **{summary['hotspots'][0]['source']}**: {summary['hotspots'][0]['emissions_tco2e']} tCOâ‚‚e ({summary['hotspots'][0]['share_pct']}%)
2. **{summary['hotspots'][1]['source']}**: {summary['hotspots'][1]['emissions_tco2e']} tCOâ‚‚e ({summary['hotspots'][1]['share_pct']}%)
3. **{summary['hotspots'][2]['source']}**: {summary['hotspots'][2]['emissions_tco2e']} tCOâ‚‚e ({summary['hotspots'][2]['share_pct']}%)

---

## 3. High-Impact Decarbonization Interventions
- **EV Fleet Electrification:** Converting 60% of fleet vehicles to Electric Vehicles will abate ~{round(summary['fleet_emissions_tco2e'] * 0.65, 1)} tCOâ‚‚e annually with an estimated financial payback of 3.8-4.5 years.
- **Rooftop Solar PV Expansion:** Deploying an additional 150 kWp solar PV array pairs directly with daytime EV charging and offsets purchased grid demand.
- **Green Commute Incentives:** Promoting subsidized EV 2-wheeler charging stations on campus mitigates Scope 3 commuter emissions.

---

## 4. Green Workforce Upskilling Matrix
- **EV Mobility:** Battery Management Systems (BMS), SAE J1772 / OCPP Charging Protocols.
- **Solar Energy:** PVSyst Microgrid Modeling, NABCEP Associate Certification.
- **ESG Governance:** ISO 14064 Carbon Footprint Auditor, GRI Certified Sustainability Professional.
"""
    
    st.markdown(report_md)
    
    st.markdown("---")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="ðŸ“¥ Download Audit Report (.md)",
            data=report_md,
            file_name=f"CarbonZero_Audit_Report_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            width='stretch'
        )
    with col_d2:
        csv_data = processed_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="ðŸ“Š Download Audited Dataset (.csv)",
            data=csv_data,
            file_name=f"Audited_Emissions_Data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            width='stretch'
        )

