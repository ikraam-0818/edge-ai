import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(
    page_title="Safety Monitor — Cloud",
    page_icon="☁️",
    layout="wide"
)

API_URL = "http://localhost:8000"

st.title("☁️ Worker Safety Monitor — Cloud Dashboard")

# ── Stats ──────────────────────────────────────────────────────────
try:
    stats = requests.get(f"{API_URL}/stats", timeout=3).json()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Readings",  stats["total_readings"])
    c2.metric("Unsafe Events",   stats["unsafe_count"])
    c3.metric("Safe Rate",       f"{stats['safe_pct']}%")
    c4.metric("Current Status",  "🚨 ALERT" if stats["unsafe_count"] > 0 else "✅ SAFE")
except Exception as e:
    st.warning("⏳ API not reachable yet — start the FastAPI server first")
    st.stop()

# ── Live charts ────────────────────────────────────────────────────
st.subheader("📈 Live Sensor Trends")
data = requests.get(f"{API_URL}/readings/latest?limit=120", timeout=3).json()

if data:
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")

    col_l, col_r = st.columns(2)
    with col_l:
        st.caption("Temperature (°C)")
        st.line_chart(df[["temperature"]].dropna(), height=200)
    with col_r:
        st.caption("Humidity (%)")
        st.line_chart(df[["humidity"]].dropna(), height=200)

# ── AI Vision & Compliance ─────────────────────────────────────────
st.subheader("⛑️ AI Vision Compliance")
if data:
    # Use the most recent reading for current compliance
    latest = data[0]
    col1, col2, col3 = st.columns(3)
    col1.metric("People Detected", latest["person_count"])
    col2.metric("Helmets Detected", latest["helmet_count"])
    col3.metric("Active Violations", latest["violations"], delta_color="inverse")

# ── Send command to Pi ─────────────────────────────────────────────
st.subheader("🎛️ Send Command to Pi")
col_a, col_b = st.columns([2, 1])
with col_a:
    command_input = st.selectbox("Action", ["reset_alarms", "reboot_camera", "update_thresholds"])
with col_b:
    if st.button("📤 Send to Pi via MQTT"):
        r = requests.post(
            f"{API_URL}/commands",
            json={"command": command_input,
                  "payload": {}},
            timeout=3
        )
        if r.status_code == 200:
            st.success("✅ Command published to EdgePi!")
        else:
            st.error("Failed to send command.")

# ── Alert history ──────────────────────────────────────────────────
st.subheader("🚨 Recent Alerts")
if data:
    alerts = [r for r in data if r["alert"] == True]
    if alerts:
        st.dataframe(
            pd.DataFrame([{
                "Time":       r["timestamp"],
                "Vibration":  r["vibration"],
                "Violations": r["violations"],
                "Temp/Hum":   f"{r['temperature']}C / {r['humidity']}%"
            } for r in alerts]),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.success("✅ No alerts in recent readings")

time.sleep(3)
st.rerun()