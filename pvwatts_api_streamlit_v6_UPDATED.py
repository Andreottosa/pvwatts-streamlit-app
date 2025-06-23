import streamlit as st
import requests

st.set_page_config(page_title="☀ PVWatts API Solar Estimator")

# --- Password protection ---
PASSWORD = st.secrets.get("app_password", "")
API_KEY = st.secrets.get("nrel_api_key", "")

st.markdown("### 🔐 Enter access password:")
input_password = st.text_input("Enter access password:", type="password")

if input_password == PASSWORD:
    st.success("🔓 Access granted.")

    st.markdown("## 🌞 PVWatts API Solar Estimator\n**(Secure Login + API Key)**")

    # Input form
    system_capacity = st.number_input("Enter Panel Size (Wp):", value=330) / 1000
    lat = st.number_input("Latitude (°):", value=-33.9700)
    lon = st.number_input("Longitude (°):", value=18.3400)
    tilt = st.number_input("Tilt Angle (°):", value=30.0)
    azimuth = st.number_input("Azimuth (°) (e.g., 0=N, 90=E, 180=S, 270=W):", value=0.0)
    losses = st.number_input("System Losses (%):", value=0.0)
    array_type = st.selectbox("Array Type:", [0, 1, 2], format_func=lambda x: ["Fixed - Roof Mount", "Fixed - Ground Mount", "Tracking"][x])
    module_type = st.selectbox("Module Type:", [0, 1, 2], format_func=lambda x: ["Standard (-15% efficiency)", "Premium (-10%)", "Thin film (-20%)"][x])

    if st.button("Run API Call"):
        if not API_KEY:
            st.error("❌ API key is missing. Please set it in Streamlit secrets or environment variables.")
        else:
            url = (
                f"https://developer.nrel.gov/api/pvwatts/v6.json?"
                f"api_key={API_KEY}&lat={lat}&lon={lon}&system_capacity={system_capacity}"
                f"&azimuth={azimuth}&tilt={tilt}&array_type={array_type}"
                f"&module_type={module_type}&losses={losses}"
            )
            try:
                r = requests.get(url)
                r.raise_for_status()
                data = r.json()
                if "outputs" in data:
                    solrad_monthly = data["outputs"]["solrad_monthly"]
                    st.success(f"🌞 Minimum: {min(solrad_monthly):.2f} kWh/m²/day in {['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][solrad_monthly.index(min(solrad_monthly))]}")
                    st.success(f"🌞 Maximum: {max(solrad_monthly):.2f} kWh/m²/day in {['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][solrad_monthly.index(max(solrad_monthly))]}")
                    st.info(f"📉 Annual Average (12 month): {data['outputs']['solrad_annual']:.2f} kWh/m²/day")
                else:
                    st.error("⚠ API returned no data.")
            except Exception as e:
                st.error(f"❌ API error: {e}")
else:
    st.warning("🔒 Access restricted. Please enter correct password.")
