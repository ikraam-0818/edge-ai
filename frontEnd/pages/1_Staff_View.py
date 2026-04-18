"""
Staff View — live camera feed with PPE detection overlay,
violation alert with captured image, and sensor readings.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

from utils.api_client import (
    health_check, get_stats, get_latest_readings,
    get_latest_frame, get_alert_frame,
)
from utils.styles import CUSTOM_CSS, COLORS
from utils.auth import require_login, sidebar_user_info

st.set_page_config(
    page_title="Staff View — Safety Monitor",
    page_icon="👷",
    layout="wide",
    initial_sidebar_state="expanded",
)
require_login()
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown("""
<style>
/* PPE badges */
.ppe-ok {
    background: linear-gradient(135deg,#0d2818,#1a472a);
    border: 2px solid #238636;
    border-radius: 14px;
    padding: 20px 16px;
    text-align: center;
    font-size: 2rem;
    font-weight: 700;
    color: #3fb950;
    margin-bottom: 10px;
}
.ppe-fail {
    background: linear-gradient(135deg,#2d0f0f,#4a1515);
    border: 2px solid #da3633;
    border-radius: 14px;
    padding: 20px 16px;
    text-align: center;
    font-size: 2rem;
    font-weight: 700;
    color: #f85149;
    animation: pulse-red 1.2s infinite;
    margin-bottom: 10px;
}
/* Camera frame wrappers */
.cam-wrap-safe {
    border: 3px solid #238636;
    border-radius: 12px;
    overflow: hidden;
    position: relative;
}
.cam-wrap-danger {
    border: 3px solid #da3633;
    border-radius: 12px;
    overflow: hidden;
    position: relative;
    animation: pulse-red 1s infinite;
}
.cam-wrap-unknown {
    border: 3px solid #30363d;
    border-radius: 12px;
    overflow: hidden;
}
/* Live / Alert badge on camera */
.cam-badge-live {
    display: inline-block;
    background: #238636;
    color: #fff;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}
.cam-badge-alert {
    display: inline-block;
    background: #da3633;
    color: #fff;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
    animation: pulse-red 1s infinite;
}
/* Violation alert box */
.violation-alert {
    background: linear-gradient(135deg,#2d0f0f,#4a1515);
    border: 2px solid #da3633;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.violation-alert .v-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #f85149;
    margin-bottom: 6px;
}
.violation-alert .v-sub {
    font-size: 0.9rem;
    color: #ffa198;
}
/* Sensor pills */
.sensor-pill {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px 18px;
    text-align: center;
    margin-bottom: 10px;
}
.sensor-pill .s-label {
    color: #8b949e;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
.sensor-pill .s-value {
    font-size: 1.5rem;
    font-weight: 700;
    margin-top: 4px;
}
/* Violations counter */
.viol-bar-safe   { background:#0d2818; border:1px solid #238636; color:#3fb950; }
.viol-bar-danger { background:#2d0f0f; border:1px solid #da3633; color:#f85149; }
.viol-bar {
    border-radius: 8px;
    padding: 10px 18px;
    margin-top: 8px;
    text-align: center;
    font-weight: 700;
    font-size: 1rem;
}
/* Camera placeholder */
.camera-placeholder {
    background: #161b22;
    border: 2px dashed #30363d;
    border-radius: 12px;
    padding: 70px 20px;
    text-align: center;
    color: #8b949e;
}
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=3_000, key="staff_refresh")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/hard-hat.png", width=60)
    st.markdown("## Safety Monitor")
    st.markdown("---")
    st.page_link("app.py",               label="🏠 Home")
    st.page_link("pages/1_Staff_View.py", label="👷 Staff View")
    st.markdown("---")
    sidebar_user_info()
    online = health_check()
    st.markdown(
        f'<span class="{"conn-online" if online else "conn-offline"}">● Backend {"online" if online else "offline"}</span>',
        unsafe_allow_html=True,
    )
    st.markdown(f"*Updated: {datetime.now().strftime('%H:%M:%S')}*")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 👷 Staff Live View")
st.markdown("**Real-time camera feed · PPE detection · Environmental sensors**")

if not online:
    st.error("Backend offline. Contact your site administrator.")
    st.stop()

# ── Fetch data ────────────────────────────────────────────────────────────────
stats       = get_stats() or {}
readings    = get_latest_readings(limit=1)
latest      = readings[0] if readings else {}
live_frame  = get_latest_frame()
alert_frame = get_alert_frame()

# ── Derive state ──────────────────────────────────────────────────────────────
status      = stats.get("current_status", latest.get("alert_level", "UNKNOWN"))
is_safe     = status == "SAFE"
is_danger   = status == "DANGER"
is_warning  = status == "WARNING"

helmet_ok   = latest.get("helmet_detected", None)
vest_ok     = latest.get("vest_detected",   None)
violations  = sum([helmet_ok is False, vest_ok is False])
reasons     = latest.get("alert_reasons", [])

# ── Status banner ─────────────────────────────────────────────────────────────
icons = {"SAFE": "✅", "WARNING": "⚠️", "DANGER": "🚨", "UNKNOWN": "❓"}
css   = {"SAFE": "status-safe", "WARNING": "status-warning", "DANGER": "status-danger"}.get(status, "status-warning")
st.markdown(
    f'<div class="{css}">{icons.get(status,"❓")} &nbsp; SITE STATUS: {status}'
    f'<span style="font-size:0.85rem;opacity:0.65;"> — {datetime.now().strftime("%H:%M:%S")}</span></div>',
    unsafe_allow_html=True,
)

# ── Violation alert box (shown only when unsafe) ──────────────────────────────
if not is_safe and violations > 0:
    violation_items = []
    if helmet_ok is False:
        violation_items.append("⛑️ &nbsp; Helmet <strong>NOT detected</strong>")
    if vest_ok is False:
        violation_items.append("🦺 &nbsp; Safety Vest <strong>NOT detected</strong>")
    items_html = "".join(
        f'<div style="margin-top:6px;font-size:0.95rem;color:#ffa198;">{item}</div>'
        for item in violation_items
    )
    st.markdown(
        f'<div class="violation-alert">'
        f'  <div class="v-title">🚨 PPE VIOLATION DETECTED</div>'
        f'  <div class="v-sub">Immediate action required — the following PPE items are missing:</div>'
        f'  {items_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Main layout: live feed | PPE + sensors ───────────────────────────────────
cam_col, info_col = st.columns([3, 2], gap="large")

# ── Live camera feed ──────────────────────────────────────────────────────────
with cam_col:

    # Badge above camera
    if is_danger or is_warning:
        st.markdown('<span class="cam-badge-alert">⚠ VIOLATION IN PROGRESS</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="cam-badge-live">● LIVE</span>', unsafe_allow_html=True)

    st.markdown("#### 📷 Live Camera Feed")

    # Pick border style based on safety status
    wrap_class = "cam-wrap-safe" if is_safe else "cam-wrap-danger"

    if live_frame:
        st.markdown(f'<div class="{wrap_class}">', unsafe_allow_html=True)
        st.image(
            live_frame,
            caption="Live feed — bounding boxes show PPE detection",
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="camera-placeholder">📷<br><br>'
            '<strong>Camera feed unavailable</strong><br>'
            'Waiting for edge device to connect…</div>',
            unsafe_allow_html=True,
        )

    # Violations counter bar
    bar_class = "viol-bar viol-bar-danger" if violations > 0 else "viol-bar viol-bar-safe"
    viol_icon = "⚠️" if violations > 0 else "✅"
    st.markdown(
        f'<div class="{bar_class}">'
        f'{viol_icon} &nbsp; PPE Violations Detected: <strong>{violations}</strong>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Latest violation capture ───────────────────────────────────────────────
    if alert_frame:
        st.markdown("---")
        st.markdown("#### 🚨 Latest Violation Capture")
        st.markdown(
            '<div style="background:#2d0f0f;border:2px solid #da3633;border-radius:10px;'
            'padding:8px 14px;margin-bottom:10px;color:#ffa198;font-size:0.85rem;">'
            '⚠️ &nbsp; This image was captured at the moment a PPE violation was detected. '
            'Review and take corrective action.'
            '</div>',
            unsafe_allow_html=True,
        )
        st.image(
            alert_frame,
            caption="Violation capture — person detected without required PPE",
            use_container_width=True,
        )

# ── PPE status + sensors ──────────────────────────────────────────────────────
with info_col:

    # ── PPE compliance badges ──────────────────────────────────────────────────
    st.markdown("#### 🦺 PPE Compliance Status")

    def _ppe_badge(label, icon, detected):
        if detected is None:
            cls, mark, note = "ppe-fail", "❓", "No data yet"
        elif detected:
            cls, mark, note = "ppe-ok",   "✅", "Detected"
        else:
            cls, mark, note = "ppe-fail",  "❌", "NOT Detected"
        return (
            f'<div class="{cls}">'
            f'  {mark} {icon} {label}<br>'
            f'  <span style="font-size:0.95rem;font-weight:400;">{note}</span>'
            f'</div>'
        )

    st.markdown(_ppe_badge("Helmet",      "⛑️",  helmet_ok), unsafe_allow_html=True)
    st.markdown(_ppe_badge("Safety Vest", "🦺",  vest_ok),   unsafe_allow_html=True)

    # ── Active alert reasons ───────────────────────────────────────────────────
    if reasons:
        st.markdown("#### ⚠️ Alert Reasons")
        for r in reasons:
            st.markdown(
                f'<div style="background:#2d1f00;border:1px solid #d29922;border-radius:8px;'
                f'padding:9px 14px;margin-bottom:6px;color:#e3b341;font-size:0.9rem;">'
                f'• &nbsp;{r.replace("_"," ").title()}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── Sensor readings ────────────────────────────────────────────────────────
    st.markdown("#### 🌡️ Environmental Sensors")

    temp = latest.get("temperature_c")
    hum  = latest.get("humidity_pct")
    gas  = latest.get("gas_ppm")
    vib  = latest.get("vibration_g")

    def _sensor_color(v, w, d):
        if v is None: return COLORS["subtext"]
        if d and v >= d: return COLORS["danger"]
        if w and v >= w: return COLORS["warning"]
        return COLORS["safe"]

    def _pill(label, value, unit, warn=None, danger=None):
        color   = _sensor_color(value, warn, danger)
        display = f"{value:.1f} {unit}" if value is not None else "N/A"
        return (
            f'<div class="sensor-pill">'
            f'  <div class="s-label">{label}</div>'
            f'  <div class="s-value" style="color:{color}">{display}</div>'
            f'</div>'
        )

    p1, p2 = st.columns(2)
    with p1:
        st.markdown(_pill("Temperature", temp, "°C",  warn=35,  danger=40),  unsafe_allow_html=True)
        st.markdown(_pill("Gas (PPM)",   gas,  "ppm", warn=300, danger=500), unsafe_allow_html=True)
    with p2:
        st.markdown(_pill("Humidity",    hum,  "%",   warn=85),              unsafe_allow_html=True)
        st.markdown(_pill("Vibration",   vib,  "g",   warn=1.5, danger=2.5), unsafe_allow_html=True)
