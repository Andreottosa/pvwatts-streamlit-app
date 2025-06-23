
import streamlit as st
import requests
import calendar

# Password protection using secrets
PASSWORD = st.secrets["app_password"]
API_KEY = st.secrets["nrel_api_key"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pw = st.text_input("Enter access password:", type="password")
    if pw == PASSWORD:
        st.session_state.authenticated = True
        st.success("🔓 Access granted.")
    else:
        st.stop()

st.title("🔆 PVWatts API Solar Estimator (Secure Login + API Key)")

array_type_map = {
    "Fixed - Open Rack": 0,
    "Fixed - Roof Mount": 1,
    "1-Axis Tracking": 2,
    "1-Axis Backtracking": 3,
    "2-Axis Tracking": 4,
}

module_type_map = {
    "Standard (~15% efficiency)": 0,
    "Premium (≥17%)": 1,
    "Thin Film (~10%)": 2,
}

def query_pvwatts_api(panel_wp, lat, lon, tilt, azimuth, losses, array_type, module_type):
    params = {
        "api_key": API_KEY,
        "lat": lat,
        "lon": lon,
        "tilt": tilt,
        "azimuth": azimuth,
        "losses": losses,
        "system_capacity": round(panel_wp / 1000, 3),
        "array_type": array_type,
        "module_type": module_type,
    }

    response = requests.get("https://developer.nrel.gov/api/pvwatts/v6.json", params=params)
    if response.status_code != 200:
        return None, f"❌ API error: {response.status_code}"

    data = response.json()
    if "outputs" not in data:
        return None, "❌ Invalid API response"

    solrad = data["outputs"]["solrad_monthly"]
    min_val = min(solrad)
    max_val = max(solrad)
    min_month = calendar.month_name[solrad.index(min_val) + 1]
    max_month = calendar.month_name[solrad.index(max_val) + 1]
    avg_min_max = round((min_val + max_val) / 2, 2)
    annual_avg = round(sum(solrad) / 12, 2)

    return {
        "min_val": min_val,
        "min_month": min_month,
        "max_val": max_val,
        "max_month": max_month,
        "avg_min_max": avg_min_max,
        "annual_avg": annual_avg,
        "monthly": solrad
    }, None

with st.form("api_form"):
    wp = st.number_input("Enter Panel Size (Wp):", min_value=10, max_value=1000, value=330)
    lat = st.number_input("Latitude (°):", value=-33.07, format="%.4f")
    lon = st.number_input("Longitude (°):", value=18.34, format="%.4f")
    tilt = st.number_input("Tilt Angle (°):", min_value=0.0, max_value=90.0, value=30.0, format="%.1f")
    azimuth = st.number_input("Azimuth (°): 0=N, 90=E, 180=S, 270=W", min_value=0.0, max_value=360.0, value=0.0, format="%.1f")
    losses = st.number_input("System Losses (%):", min_value=0.0, max_value=100.0, value=0.0, format="%.1f")

    array_type_label = st.selectbox("Array Type:", list(array_type_map.keys()), index=1)
    module_type_label = st.selectbox("Module Type:", list(module_type_map.keys()), index=0)

    submitted = st.form_submit_button("Run API Call")

if submitted:
    array_type_val = array_type_map[array_type_label]
    module_type_val = module_type_map[module_type_label]

    with st.spinner("Querying PVWatts API..."):
        result, error = query_pvwatts_api(wp, lat, lon, tilt, azimuth, losses, array_type_val, module_type_val)
        if error:
            st.error(error)
        else:
            st.success(f"☀️ Minimum: {result['min_val']} kWh/m²/day in {result['min_month']}")
            st.success(f"☀️ Maximum: {result['max_val']} kWh/m²/day in {result['max_month']}")
            st.info(f"📆 Annual Average (12-month): {result['annual_avg']} kWh/m²/day")
            st.info(f"📊 Average of Min + Max: {result['avg_min_max']} kWh/m²/day")
