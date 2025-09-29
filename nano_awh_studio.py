import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------
# Demo material database with sorbent costs
# -------------------------------
materials = pd.DataFrame({
    "Material": ["MOF-303", "Silica Gel", "Graphene Oxide"],
    "q_max_g_g": [0.45, 0.25, 0.30],     # max uptake g water / g sorbent
    "RH50_q_g_g": [0.35, 0.15, 0.20],    # uptake at 50% RH
    "regen_T_C": [70, 90, 80],           # regeneration temperature
    "energy_kJ_g": [2.5, 3.0, 2.8],      # heat of desorption (kJ per g water)
    "cost_USD_kg": [150, 3, 20]          # material cost (USD/kg, demo values)
})

# -------------------------------
# Electricity Prices by Country (USD/kWh)
# -------------------------------
country_data = {
    "USA": 0.15,
    "Saudi Arabia": 0.05,
    "UAE": 0.10,
    "Jordan": 0.18,
    "Germany": 0.30,
}

# -------------------------------
# Sidebar Inputs with Tooltips
# -------------------------------
st.sidebar.title("⚙️ Simulation Controls")

material_choice = st.sidebar.selectbox(
    "Select Sorbent Material", 
    materials["Material"],
    help="Choose which sorbent to simulate. MOFs = high capacity, silica gel = cheap but less efficient, GO = moderate."
)

m_sorbent = st.sidebar.slider(
    "Sorbent Mass (kg)", 0.1, 100.0, 5.0,
    help="Mass of sorbent. Larger mass captures more water but adds cost and weight."
)
st.sidebar.caption("✅ Recommended: 0.5 – 50 kg")

rh = st.sidebar.slider(
    "Relative Humidity (%)", 5, 95, 40,
    help="Ambient humidity. Higher RH increases uptake; below 20% is challenging."
)
st.sidebar.caption("✅ Recommended: 20 – 80 %")

temp = st.sidebar.slider(
    "Air Temperature (°C)", 0, 50, 25,
    help="Ambient temperature. Affects adsorption and regeneration efficiency."
)
st.sidebar.caption("✅ Recommended: 15 – 40 °C")

cycles = st.sidebar.slider(
    "Cycles per Day", 1, 10, 2,
    help="Number of adsorption–desorption cycles in 24h. Passive ≈1, active ≈2–4, very active >4."
)
st.sidebar.caption("✅ Recommended: 1 – 4 cycles/day")

country_choice = st.sidebar.selectbox(
    "🌍 Select Country (Electricity Price)",
    list(country_data.keys()),
    help="Select country to auto-load electricity price for regeneration."
)
energy_price = country_data[country_choice]   # USD/kWh

bottled_price = st.sidebar.number_input(
    "💧 Bottled Water Reference Price (USD/L)",
    0.10, 5.00, 0.50, step=0.10,
    help="Benchmark bottled water price for comparison."
)

# -------------------------------
# Input Warnings
# -------------------------------
if not (20 <= rh <= 80):
    st.warning("⚠️ RH outside realistic range (20–80%). Results may be unrealistic.")
if not (15 <= temp <= 40):
    st.warning("⚠️ Temperature outside realistic range (15–40 °C).")
if not (0.5 <= m_sorbent <= 50):
    st.warning("⚠️ Sorbent mass outside practical range (0.5–50 kg).")
if not (1 <= cycles <= 4):
    st.warning("⚠️ Cycle count outside practical range (1–4 per day).")

# -------------------------------
# Helper: adsorption isotherm model (simplified linear)
# -------------------------------
def uptake_isotherm(RH, q_max, RH50_q):
    return min(q_max, (RH / 50.0) * RH50_q)

# -------------------------------
# Simulation
# -------------------------------
row = materials[materials["Material"] == material_choice].iloc[0]
q_ads = uptake_isotherm(rh, row.q_max_g_g, row.RH50_q_g_g)   # g/g uptake
water_adsorbed_g = q_ads * m_sorbent * 1000                  # grams water
water_per_cycle_L = water_adsorbed_g / 1000                  # liters per cycle
daily_yield_L = water_per_cycle_L * cycles
annual_yield_L = daily_yield_L * 365

# Energy calculations
energy_kJ = row.energy_kJ_g * water_adsorbed_g               # kJ per cycle
energy_kWh = energy_kJ / 3600
energy_per_L = energy_kJ / (water_per_cycle_L + 1e-9)        # kJ/L

# Cost calculations
sorbent_cost = row.cost_USD_kg * m_sorbent
days_lifetime = 365 * 3   # assume 3-year sorbent lifetime
total_cycles_lifetime = days_lifetime * cycles
lifetime_water_L = water_per_cycle_L * total_cycles_lifetime
sorbent_cost_per_L = sorbent_cost / max(lifetime_water_L, 1e-9)

energy_cost_cycle = energy_kWh * energy_price
energy_cost_per_L = energy_cost_cycle / max(water_per_cycle_L, 1e-9)

total_cost_per_L = energy_cost_per_L + sorbent_cost_per_L

# -------------------------------
# Main UI
# -------------------------------
st.title("💧 Nanotech Atmospheric Water Harvesting Studio")
st.markdown("Simulate water yield, energy, and cost of production for nanotech-based AWH materials.")

# Show results
st.subheader("📊 Results")
st.write(f"**Material:** {material_choice}")
st.write(f"**Water per Cycle:** {water_per_cycle_L:.2f} L")
st.write(f"**Daily Yield:** {daily_yield_L:.2f} L/day")
st.write(f"**Annual Yield:** {annual_yield_L:.0f} L/year")
st.write(f"**Regeneration Temperature:** {row.regen_T_C} °C")
st.write(f"**Energy Required:** {energy_kJ:.1f} kJ per cycle ({energy_kWh:.2f} kWh)")
st.write(f"**Specific Energy:** {energy_per_L:.1f} kJ per liter (~{energy_per_L/3600:.3f} kWh/L)")
st.write(f"**Electricity Price (from {country_choice}):** ${energy_price:.2f}/kWh")
st.write(f"**Reference Bottled Water Price:** ${bottled_price:.2f}/L")
st.write(f"**Cost of Production:** ${total_cost_per_L:.2f}/L")

# Comparison to bottled water
if total_cost_per_L < bottled_price:
    st.success(f"✅ Production cost is cheaper than bottled water (${bottled_price:.2f}/L).")
else:
    st.error(f"❌ Production cost is higher than bottled water (${bottled_price:.2f}/L).")

# -------------------------------
# Validation Table with Colors + Emoji
# -------------------------------
st.subheader("✅ Parameter Check vs Recommended Ranges")

def check_range(value, min_val, max_val, tol=0.05):
    if min_val <= value <= max_val:
        span = max_val - min_val
        lower_band = min_val + tol * span
        upper_band = max_val - tol * span
        if value < lower_band or value > upper_band:
            return "⚠️ Borderline"
        return "✅ OK"
    else:
        return "❌ Outside"

validation_data = {
    "Parameter": ["Relative Humidity (%)", "Air Temperature (°C)", "Sorbent Mass (kg)", "Cycles per Day"],
    "Your Value": [rh, temp, m_sorbent, cycles],
    "Recommended Range": ["20 – 80", "15 – 40", "0.5 – 50", "1 – 4"],
    "Status": [
        check_range(rh, 20, 80),
        check_range(temp, 15, 40),
        check_range(m_sorbent, 0.5, 50),
        check_range(cycles, 1, 4),
    ]
}

validation_df = pd.DataFrame(validation_data)

def highlight_status(val):
    if "✅" in val:
        color = "lightgreen"
    elif "⚠️" in val:
        color = "khaki"
    else:
        color = "salmon"
    return f"background-color: {color}"

st.dataframe(validation_df.style.applymap(highlight_status, subset=["Status"]))

# -------------------------------
# Plot isotherm curve
# -------------------------------
st.subheader("📈 Adsorption Isotherm (Demo)")
RH_range = np.linspace(0, 90, 50)
uptake_curve = [uptake_isotherm(r, row.q_max_g_g, row.RH50_q_g_g) for r in RH_range]
fig, ax = plt.subplots(figsize=(4,3))
ax.plot(RH_range, uptake_curve, label=f"{material_choice}")
ax.scatter([rh], [q_ads], color="red", label="Operating Point")
ax.set_xlabel("Relative Humidity (%)")
ax.set_ylabel("Uptake (g water / g sorbent)")
ax.set_title("Isotherm Curve")
ax.legend()
st.pyplot(fig)

# -------------------------------
# Show Recommended Parameter Ranges
# -------------------------------
st.markdown("""
### 📐 Recommended Input Ranges
- **Relative Humidity:** 20 – 80 %  
- **Air Temperature:** 15 – 40 °C  
- **Sorbent Mass:** 0.5 – 50 kg  
- **Cycles per Day:** 1 – 4  
- **Water Uptake:** 0.1 – 0.5 g/g (depends on material)  
- **Regeneration Temperature:** 60 – 100 °C  
- **Energy per Liter:** 1,000 – 10,000 kJ/L (≈0.3 – 3 kWh/L)  

⚠️ Values outside these ranges may give **unrealistic yields**.
""")
