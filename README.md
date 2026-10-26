# 🌱 CarbonZero: Autonomous Sustainability & EV Transition Copilot

> **An AI Agent for Campus & Enterprise Carbon Footprint Auditing, EV Fleet Optimization, and Green Skills Advisory.**  
> Aligned with **Edunet Green Skills & Electric Mobility Innovation Framework**.

---

## 📌 Project Overview

**CarbonZero** is an intelligent AI Agent system designed to help academic campuses, corporate tech parks, and municipal institutions transition towards net-zero emissions. 

It combines **GHG Protocol Corporate Standard** carbon accounting with an interactive **Electric Vehicle (EV) Fleet Transition Simulator** and an **Autonomous Green Skills Advisory Agent**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CarbonZero Architecture                         │
└────────────────────────────────────────────────────────────────────────┘
          ▲                                           ▲
          │                                           │
  ┌───────────────┐                           ┌───────────────┐
  │ Resource Logs │                           │ User Prompts  │
  │ (Grid, Fleet, │                           │  & Scenarios  │
  │  Solar, Waste)│                           └───────┬───────┘
  └───────┬───────┘                                   │
          │                                           ▼
          ▼                           ┌───────────────────────────────┐
  ┌───────────────┐                   │    CarbonZero AI Copilot      │
  │ GHG Protocol  │                   │ (Autonomous Multi-Tool Agent) │
  │ Scope 1, 2, 3 │                   └───────┬───────────────┬───────┘
  │  Calculator   │                           │               │
  └───────┬───────┘                           ▼               ▼
          │                   ┌──────────────────┐ ┌──────────────────┐
          │                   │ EV Fleet & Solar │ │   Green Skills   │
          │                   │ Microgrid Sim    │ │  Career Database │
          │                   └──────────────────┘ └──────────────────┘
          ▼                                           │
  ┌───────────────────────────────────────────────────▼───────────────┐
  │        Interactive Streamlit Sustainability Dashboard             │
  │  • Scope 1/2/3 KPIs       • EV Payback & ROI    • Audit Reports   │
  └───────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Features

### 1. 📊 GHG Protocol Scope 1, 2, & 3 Carbon Auditing
- **Scope 1 (Direct Emissions):** Diesel generators, captive petrol/diesel fleet, canteen LPG.
- **Scope 2 (Indirect Emissions):** Purchased grid electricity with configurable regional grid emission factors (default: CEA India average of $0.713 \text{ kg CO}_2e/\text{kWh}$).
- **Scope 3 (Value Chain):** Employee passenger-km commute, business air travel, and landfill solid waste.
- **Automated Hotspot Identification:** Instantly ranks and highlights top carbon emission sources.

### 2. ⚡ EV Fleet Transition & Solar Microgrid Simulator
- **Techno-Economic Modeling:** Simulates converting ICE fleets (shuttles, delivery vans, pool cars) to electric vehicles.
- **Solar Microgrid Synergy:** Models charging EVs via rooftop solar PV versus standard grid power.
- **Financial Payback & ROI:** Calculates CapEx (vehicles + Level-2 AC and DC Fast chargers), OpEx savings (fuel vs electricity + maintenance), and payback period in years.

### 3. 🤖 Autonomous CarbonZero AI Agent
Equipped with dynamic tools:
- `tool_diagnose_emissions()`: Evaluates carbon telemetry and identifies hotspots.
- `tool_simulate_ev()`: Evaluates custom electrification percentages and solar charging parameters.
- `tool_recommend_actions()`: Generates prioritized decarbonization actions with estimated carbon abatement.
- `tool_recommend_green_skills()`: Recommends in-demand green skills, global certifications, and job roles.

### 4. 🎓 Green Skills & Workforce Advisory
Provides structured upskilling tracks across 4 green domains:
1. **EV & E-Mobility:** Battery Management Systems (BMS), OCPP Charging Protocols, SAE J1772 High Voltage Safety.
2. **Clean Energy:** Solar PV Sizing (PVSyst), Battery Energy Storage Systems (BESS), NABCEP certifications.
3. **ESG & Carbon Auditing:** GHG Protocol, ISO 14064, BRSR framework, GRI credentials.
4. **Smart Facilities:** HVAC Variable Speed Drives, Building Automation (BMS/IoT), LEED/GRIHA.

### 5. 📑 Executive ESG Sustainability Audit Report
- One-click generation of a standardized audit report adhering to **ISO 14064** and **GHG Protocol** standards.
- Downloadable in **Markdown (.md)** and audited **CSV (.csv)** formats.

---

## 🛠️ Project Structure

```
d:\Edunet_Project\
├── app.py                      # Main Streamlit dashboard & UI
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation & Edunet pitch
├── core/
│   ├── __init__.py             # Package init
│   ├── calculator.py           # GHG Protocol Scope 1-2-3 math & emission factors
│   ├── simulator.py            # EV fleet transition, charging infra, & payback engine
│   ├── agent.py                # CarbonZero autonomous agent & green skills database
│   └── data_generator.py       # Realistic 12-month campus telemetry generator
└── data/
    └── sample_campus_emissions.csv  # Pre-bundled 12-month campus dataset
```

---

## 💻 Installation & Setup

### 1. Prerequisites
- Python 3.9, 3.10, 3.11, or 3.12 installed on your system.

### 2. Install Dependencies
Open your terminal or PowerShell in the project directory:
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
streamlit run app.py
```
The application will automatically open in your default browser at `http://localhost:8501`.

---

## 🎯 Edunet Presentation & Hackathon Pitch Points

When presenting this project to evaluators:

1. **Problem Statement:** 
   *"Institutions and campuses want to achieve net-zero, but lack unified tools to measure their Scope 1-3 footprint, evaluate the financial feasibility of switching to electric vehicles, and upskill their students/staff in green tech."*

2. **The Solution:** 
   *"CarbonZero is an autonomous AI agent that ingests operational telemetry, audits emissions according to international GHG Protocol standards, simulates EV fleet conversions with solar microgrids, and guides workforce upskilling with customized green skill pathways."*

3. **Innovation & Green Skills Alignment:**
   - Highlights the dual benefit of EV adoption: carbon reduction + operational cost savings.
   - Bridges the gap between carbon accounting and green talent development (Green Skills).
   - 100% reproducible and ready to deploy with both synthetic preloaded data and real CSV uploads.

---

## 📜 License
Developed for educational, research, and sustainability innovation purposes as part of the Edunet Foundation initiative.
