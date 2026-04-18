"""
Control Panel page – send commands to the edge device and simulate readings.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import random
from datetime import datetime

from utils.api_client import health_check, get_stats, send_command, send_reading
from utils.styles import CUSTOM_CSS, COLORS
from utils.auth import require_admin, sidebar_user_info

st.set_page_config(page_title="Control Panel — Safety Monitor", page_icon="🎛️", layout="wide")
require_admin()
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Safety Monitor")
    st.markdown("---")
    st.page_link("app.py",                        label="🏠 Home")
    st.page_link("pages/1_Staff_View.py",          label="👷 Staff View")
    st.page_link("pages/2_Admin_View.py",          label="🔐 Admin View")
    st.page_link("pages/3_Analytics.py",           label="📈 Analytics")
    st.page_link("pages/4_Alerts.py",              label="🚨 Alert Log")
    st.page_link("pages/5_Control.py",             label="🎛️  Control Panel")
    st.markdown("---")
    sidebar_user_info()
    online = health_check()
    if online:
        st.markdown('<span class="conn-online">● Backend online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="conn-offline">● Backend offline</span>', unsafe_allow_html=True)
    st.markdown(f"*{datetime.now().strftime('%H:%M:%S')}*")

st.markdown("# 🎛️ Control Panel")
st.markdown("Send commands to the edge device and manage system configuration.")

if not online:
    st.error("Backend offline. Start with `uvicorn cloud.main:app --reload`.")
    st.stop()

stats = get_stats() or {}

# ── System status card ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## System Status")

c1, c2, c3 = st.columns(3)
c1.metric("Total Readings",  stats.get("total_readings", 0))
c2.metric("Unsafe Events",   stats.get("unsafe_count", 0))
c3.metric("Current Status",  stats.get("current_status", "UNKNOWN"))

st.markdown("---")

# ── Quick commands ────────────────────────────────────────────────────────────
st.markdown("## Quick Commands")
st.markdown("Send a command to the edge device. Commands are queued and delivered on next poll.")

# Emergency stop — prominent and separate
st.markdown(
    '<div style="background:#2d0f0f;border:2px solid #da3633;border-radius:10px;padding:16px 22px;margin-bottom:16px;">'
    '<span style="color:#f85149;font-size:1.1rem;font-weight:700;">⚠️ Emergency Stop</span>'
    '<span style="color:#8b949e;font-size:0.9rem;"> — halts all inference and triggers alarm on the edge device</span>'
    '</div>',
    unsafe_allow_html=True,
)
if st.button("🛑 EMERGENCY STOP", type="primary", use_container_width=False):
    ok = send_command("EMERGENCY_STOP")
    if ok:
        st.error("EMERGENCY STOP sent — edge device halting.")
    else:
        st.error("Failed to send command.")

st.markdown("---")

q1, q2, q3, q4 = st.columns(4)

with q1:
    if st.button("🔔 Test Alarm", use_container_width=True):
        ok = send_command("TEST_ALARM", {"duration_s": 3})
        if ok:
            st.success("Command queued: TEST_ALARM")
        else:
            st.error("Failed to send.")

with q2:
    if st.button("✅ Reset Safe", use_container_width=True):
        ok = send_command("RESET_SAFE")
        if ok:
            st.success("Command queued: RESET_SAFE")
        else:
            st.error("Failed to send.")

with q3:
    if st.button("📸 Capture Frame", use_container_width=True):
        ok = send_command("CAPTURE_FRAME")
        if ok:
            st.success("Command queued: CAPTURE_FRAME")
        else:
            st.error("Failed to send.")

with q4:
    if st.button("♻️ Restart Vision", use_container_width=True):
        ok = send_command("RESTART_VISION")
        if ok:
            st.success("Command queued: RESTART_VISION")
        else:
            st.error("Failed to send.")

st.markdown("---")

# ── Threshold configuration ───────────────────────────────────────────────────
st.markdown("## Threshold Configuration")

t1, t2, t3 = st.columns(3)

with t1:
    st.markdown("### Temperature (°C)")
    temp_threshold = st.slider(
        "Temp alert level", min_value=20, max_value=60, value=35, step=1,
        help="Above this triggers WARNING (FR-5: 35 °C default).",
    )
    if st.button("Set Temp Threshold", type="primary", key="btn_temp"):
        ok = send_command("SET_TEMP_THRESHOLD", {"celsius": temp_threshold})
        st.success(f"Temp threshold → {temp_threshold} °C.") if ok else st.error("Failed.")

with t2:
    st.markdown("### Gas Alert (PPM)")
    gas_threshold = st.slider(
        "Gas PPM alert level", min_value=100, max_value=1000, value=300, step=25,
        help="Above this triggers WARNING.",
    )
    if st.button("Set Gas Threshold", type="primary", key="btn_gas"):
        ok = send_command("SET_GAS_THRESHOLD", {"ppm": gas_threshold})
        st.success(f"Gas threshold → {gas_threshold} PPM.") if ok else st.error("Failed.")

with t3:
    st.markdown("### Vibration (g)")
    vib_threshold = st.slider(
        "Vibration alert level (g)", min_value=0.5, max_value=5.0, value=1.5, step=0.1,
        help="Above this triggers WARNING.",
    )
    if st.button("Set Vibration Threshold", type="primary", key="btn_vib"):
        ok = send_command("SET_VIB_THRESHOLD", {"g": vib_threshold})
        st.success(f"Vibration threshold → {vib_threshold} g.") if ok else st.error("Failed.")

st.markdown("---")

# ── Custom command ────────────────────────────────────────────────────────────
st.markdown("## Custom Command")
st.markdown("Send an arbitrary command string with an optional JSON payload.")

with st.form("custom_cmd"):
    cmd_name    = st.text_input("Command name",    placeholder="e.g. SET_CONFIDENCE")
    payload_key = st.text_input("Payload key",     placeholder="e.g. threshold")
    payload_val = st.text_input("Payload value",   placeholder="e.g. 0.6")
    submitted   = st.form_submit_button("Send Command", type="primary")
    if submitted:
        if not cmd_name.strip():
            st.warning("Command name cannot be empty.")
        else:
            payload = {payload_key: payload_val} if payload_key else {}
            ok = send_command(cmd_name.strip().upper(), payload)
            if ok:
                st.success(f"Command `{cmd_name.upper()}` queued successfully.")
            else:
                st.error("Failed to queue command.")

st.markdown("---")

# ── Simulation / testing ──────────────────────────────────────────────────────
st.markdown("## Simulate a Reading")
st.markdown(
    "Inject a synthetic sensor reading into the backend (useful for testing the dashboard "
    "before the Raspberry Pi is connected)."
)

with st.form("simulate"):
    sc1, sc2 = st.columns(2)
    with sc1:
        sim_helmet  = st.checkbox("Helmet detected",  value=True)
        sim_vest    = st.checkbox("Vest detected",    value=True)
        sim_safe    = st.checkbox("Is safe",          value=True)
        sim_level   = st.selectbox("Alert level", ["SAFE", "WARNING", "DANGER"])
    with sc2:
        sim_temp    = st.number_input("Temperature (°C)", value=27.0, step=0.5)
        sim_humidity= st.number_input("Humidity (%)",     value=55.0, step=1.0)
        sim_gas     = st.number_input("Gas (PPM)",        value=50.0,  step=10.0)
        sim_vib     = st.number_input("Vibration (g)",    value=0.1,  step=0.1)

    sim_reasons_raw = st.text_input(
        "Alert reasons (comma-separated)", placeholder="e.g. high_temperature,no_helmet"
    )

    btn_col1, btn_col2 = st.columns(2)
    send_sim    = btn_col1.form_submit_button("Inject Reading",          type="primary", use_container_width=True)
    send_random = btn_col2.form_submit_button("Inject 10 Random Readings", use_container_width=True)

if send_sim:
    reasons = [r.strip() for r in sim_reasons_raw.split(",") if r.strip()]
    payload = {
        "helmet_detected": sim_helmet,
        "vest_detected":   sim_vest,
        "temperature_c":   float(sim_temp),
        "humidity_pct":    float(sim_humidity),
        "gas_ppm":         float(sim_gas),
        "vibration_g":     float(sim_vib),
        "is_safe":         sim_safe,
        "alert_level":     sim_level,
        "alert_reasons":   reasons,
    }
    result = send_reading(payload)
    if result:
        st.success(f"Reading injected. ID: {result.get('id')} | Anomaly: {result.get('anomaly', {})}")
    else:
        st.error("Failed to inject reading.")

if send_random:
    for _ in range(10):
        lvl = random.choice(["SAFE", "SAFE", "SAFE", "WARNING", "DANGER"])
        send_reading({
            "helmet_detected": random.random() > 0.2,
            "vest_detected":   random.random() > 0.3,
            "temperature_c":   round(random.uniform(22, 45), 1),
            "humidity_pct":    round(random.uniform(40, 90), 1),
            "gas_ppm":         round(random.uniform(0, 600), 1),
            "vibration_g":     round(random.uniform(0, 3), 2),
            "is_safe":         lvl == "SAFE",
            "alert_level":     lvl,
            "alert_reasons":   [] if lvl == "SAFE" else [random.choice(
                ["high_temperature", "high_gas", "no_helmet", "high_vibration"]
            )],
        })
    st.success("10 random readings injected. Refresh the Overview page.")
