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
    c4.metric("Current Status",  stats["current_status"])
except:
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
        st.caption("Gas (ppm)")
        st.line_chart(df[["gas_ppm"]].dropna(), height=200)
        st.caption("Vibration (g)")
        st.line_chart(df[["vibration_g"]].dropna(), height=200)
    with col_r:
        st.caption("Temperature (°C)")
        st.line_chart(df[["temperature_c"]].dropna(), height=200)
        st.caption("Humidity (%)")
        st.line_chart(df[["humidity_pct"]].dropna(), height=200)

# ── PPE compliance ─────────────────────────────────────────────────
st.subheader("⛑️ PPE Compliance")
if data:
    total      = len(data)
    helmet_ok  = sum(1 for r in data if r["helmet_detected"])
    vest_ok    = sum(1 for r in data if r["vest_detected"])
    col1, col2 = st.columns(2)
    col1.metric("Helmet compliance", f"{helmet_ok}/{total}",
                f"{helmet_ok/total*100:.0f}%")
    col2.metric("Vest compliance",   f"{vest_ok}/{total}",
                f"{vest_ok/total*100:.0f}%")

# ── Send command to Pi ─────────────────────────────────────────────
st.subheader("🎛️ Send Command to Pi")
col_a, col_b = st.columns([2, 1])
with col_a:
    threshold = st.slider("Gas alert threshold (ppm)", 100, 800, 300, 50)
with col_b:
    if st.button("📤 Send to Pi"):
        r = requests.post(
            f"{API_URL}/commands",
            json={"command": "set_gas_threshold",
                  "payload": {"threshold_ppm": threshold}},
            timeout=3
        )
        if r.status_code == 200:
            st.success("✅ Command queued!")

# ── Alert history ──────────────────────────────────────────────────
st.subheader("🚨 Recent Alerts")
if data:
    alerts = [r for r in data if not r["is_safe"]]
    if alerts:
        st.dataframe(
            pd.DataFrame([{
                "Time":   r["timestamp"],
                "Level":  r["alert_level"],
                "Issues": " | ".join(r["alert_reasons"])
            } for r in alerts]),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.success("✅ No alerts in recent readings")

time.sleep(3)
st.rerun()