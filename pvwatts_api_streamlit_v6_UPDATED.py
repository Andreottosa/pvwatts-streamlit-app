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

    # --- Input Form ---
    with st.form(key="input_form"):
        system_capacity = st.number_input("Enter Panel Size (kWp):", min_value=0.05, value=1.0)
        lat = st.number_input("Latitude (°):", value=-33.9700)
        lon = st.number_input("Longitude (°):", value=18.3400)
        tilt = st.number_input("Tilt Angle (°):", value=30.0)
        azimuth = st.number_input("Azimuth (°) (0=N, 90=E, 180=S, 270=W):", value=0.0)
        losses = st.number_input("System Losses (%):", min_value=0.0, max_value=100.0, value=0.0)
        
        array_type = st.selectbox(
            "Array Type:",
            [0, 1, 2],
            format_func=lambda x: ["Fixed - Roof Mount", "Fixed - Ground Mount", "Tracking"][x]
        )
        module_type = st.selectbox(
            "Module Type:",
            [0, 1, 2],
            format_func=lambda x: ["Standard (-15%)", "Premium (-10%)", "Thin film (-20%)"][x]
        )

        submit_button = st.form_submit_button("Run API Call")

    # --- API Call on Submit ---
    if submit_button:
        if not API_KEY:
            st.error("❌ API key is missing. Please set it in Streamlit secrets.")
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
                    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
                    min_val = min(solrad_monthly)
                    max_val = max(solrad_monthly)
                    avg_min_max = (min_val + max_val) / 2

                    st.success(f"🌞 Minimum: {min_val:.2f} kWh/m²/day in {months[solrad_monthly.index(min_val)]}")
                    st.success(f"🌞 Maximum: {max_val:.2f} kWh/m²/day in {months[solrad_monthly.index(max_val)]}")
                    st.success(f"📊 Average of Min & Max: {avg_min_max:.2f} kWh/m²/day")
                    st.info(f"📉 Annual Average (12 month): {data['outputs']['solrad_annual']:.2f} kWh/m²/day")
                else:
                    st.error("⚠ API returned no data.")
            except Exception as e:
                st.error(f"❌ API error: {e}")

else:
    st.warning("🔒 Access restricted. Please enter correct password.")
