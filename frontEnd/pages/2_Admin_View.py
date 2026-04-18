"""
Admin / Manager View — full dashboard: live feed, PPE status, sensors,
Safety Compliance % chart (24 h), alert summary, and quick controls.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from utils.api_client import (
    health_check, get_stats, get_latest_readings,
    get_latest_frame, get_alert_frame, send_command,
)
from utils.styles import CUSTOM_CSS, COLORS, PLOTLY_LAYOUT
from utils.auth import require_admin, sidebar_user_info

st.set_page_config(
    page_title="Admin View — Safety Monitor",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)
require_admin()
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown("""
<style>
.ppe-ok {
    background: linear-gradient(135deg,#0d2818,#1a472a);
    border: 2px solid #238636;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    font-size: 1.6rem;
    font-weight: 700;
    color: #3fb950;
    margin-bottom: 8px;
}
.ppe-fail {
    background: linear-gradient(135deg,#2d0f0f,#4a1515);
    border: 2px solid #da3633;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    font-size: 1.6rem;
    font-weight: 700;
    color: #f85149;
    animation: pulse-red 1.2s infinite;
    margin-bottom: 8px;
}
.camera-placeholder {
    background: #161b22;
    border: 2px dashed #30363d;
    border-radius: 12px;
    padding: 50px 20px;
    text-align: center;
    color: #8b949e;
}
.factory-header {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 12px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
}
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=3_000, key="admin_refresh")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/hard-hat.png", width=60)
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
    st.markdown(f"*Updated: {datetime.now().strftime('%H:%M:%S')}*")

# ── Factory header ────────────────────────────────────────────────────────────
health_label = "Online, Good" if online else "Offline"
health_color = COLORS["safe"] if online else COLORS["danger"]
st.markdown(
    f'<div class="factory-header">'
    f'  <span style="color:#8b949e;font-size:0.85rem;">🏭 <strong style="color:#e6edf3;">FACTORY LOCATION:</strong> Plant A, Building 3</span>'
    f'  <span style="color:#8b949e;font-size:0.85rem;">💻 <strong style="color:#e6edf3;">DEVICE HEALTH:</strong> '
    f'<span style="color:{health_color};">[{health_label}]</span></span>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown("# 🔐 Admin / Manager View")
st.markdown("**Full system overview — live feed, compliance, history & controls**")

if not online:
    st.error("Backend offline. Start with `uvicorn cloud.app:app --reload`.")
    st.stop()

# ── Data fetch ────────────────────────────────────────────────────────────────
stats       = get_stats() or {}
readings    = get_latest_readings(limit=200)
latest      = readings[-1] if readings else {}
frame       = get_latest_frame()
alert_frame = get_alert_frame()

is_safe   = stats.get("current_status", "UNKNOWN") == "SAFE"
violations = sum([
    latest.get("helmet_detected", True) is False,
    latest.get("vest_detected",   True) is False,
])

# ── Status banner ─────────────────────────────────────────────────────────────
status = stats.get("current_status", latest.get("alert_level", "UNKNOWN"))
icons  = {"SAFE": "✅", "WARNING": "⚠️", "DANGER": "🚨", "UNKNOWN": "❓"}
css    = {"SAFE": "status-safe", "WARNING": "status-warning", "DANGER": "status-danger"}.get(status, "status-warning")

st.markdown(
    f'<div class="{css}">{icons.get(status,"❓")} &nbsp; SITE STATUS: {status}</div>',
    unsafe_allow_html=True,
)

# KPI row
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Readings",  f"{stats.get('total_readings', 0):,}")
c2.metric("Unsafe Events",   f"{stats.get('unsafe_count', 0):,}")
c3.metric("Safe Rate",       f"{stats.get('safe_pct', 0.0):.1f}%")
c4.metric("Temperature",     f"{latest.get('temperature_c', '--')} °C" if latest.get('temperature_c') is not None else "--")
c5.metric("Humidity",        f"{latest.get('humidity_pct', '--')} %" if latest.get('humidity_pct') is not None else "--")

st.markdown("---")

# ── Section 1: Camera + PPE status ───────────────────────────────────────────
st.markdown("## 📷 Live Camera Feed & PPE Status")
cam_col, ppe_col = st.columns([3, 2], gap="large")

with cam_col:
    badge = '<span style="background:#da3633;color:#fff;font-size:0.75rem;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:0.08em;">⚠ VIOLATION IN PROGRESS</span>' if not is_safe else '<span style="background:#238636;color:#fff;font-size:0.75rem;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:0.08em;">● LIVE</span>'
    st.markdown(badge, unsafe_allow_html=True)

    border = "#da3633" if not is_safe else "#238636"
    if frame:
        st.markdown(f'<div style="border:3px solid {border};border-radius:12px;overflow:hidden;">', unsafe_allow_html=True)
        st.image(frame, caption="Live feed — bounding boxes show PPE detection", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="camera-placeholder">📷<br><br>'
            '<strong>Camera feed unavailable</strong><br>'
            'Waiting for edge device…</div>',
            unsafe_allow_html=True,
        )

    viol_color = COLORS["danger"] if violations > 0 else COLORS["safe"]
    viol_bg    = "#2d0f0f"        if violations > 0 else "#0d2818"
    st.markdown(
        f'<div style="background:{viol_bg};border:1px solid {viol_color};border-radius:8px;'
        f'padding:10px 18px;margin-top:8px;text-align:center;'
        f'color:{viol_color};font-weight:700;font-size:1rem;">'
        f'{"⚠️" if violations > 0 else "✅"} &nbsp; PPE Violations Detected: {violations}</div>',
        unsafe_allow_html=True,
    )

    if alert_frame:
        st.markdown("---")
        st.markdown("**🚨 Latest Violation Capture**")
        st.markdown(
            '<div style="background:#2d0f0f;border:2px solid #da3633;border-radius:10px;'
            'padding:8px 14px;margin-bottom:8px;color:#ffa198;font-size:0.82rem;">'
            '⚠️ &nbsp; Captured at moment of PPE violation — review and take action.'
            '</div>',
            unsafe_allow_html=True,
        )
        st.image(alert_frame, caption="Violation capture", use_container_width=True)

with ppe_col:
    st.markdown("### 🦺 PPE Compliance")
    helmet_ok = latest.get("helmet_detected", None)
    vest_ok   = latest.get("vest_detected",   None)

    def _ppe_badge(label, icon, detected):
        if detected is None:
            css_cls, mark, note = "ppe-fail", "❓", "No data"
        elif detected:
            css_cls, mark, note = "ppe-ok",   "✅", "Detected"
        else:
            css_cls, mark, note = "ppe-fail",  "❌", "NOT Detected"
        return (
            f'<div class="{css_cls}">{mark} {icon} {label}<br>'
            f'<span style="font-size:0.9rem;font-weight:400;">{note}</span></div>'
        )

    st.markdown(_ppe_badge("Helmet",      "⛑️",  helmet_ok), unsafe_allow_html=True)
    st.markdown(_ppe_badge("Safety Vest", "🦺",  vest_ok),   unsafe_allow_html=True)

    # Sensor snapshot
    st.markdown("### 🌡️ Sensor Snapshot")
    temp = latest.get("temperature_c")
    hum  = latest.get("humidity_pct")
    gas  = latest.get("gas_ppm")
    vib  = latest.get("vibration_g")

    def _color(v, w, d):
        if v is None: return COLORS["subtext"]
        if d and v >= d: return COLORS["danger"]
        if w and v >= w: return COLORS["warning"]
        return COLORS["safe"]

    def _card(label, value, unit, w=None, d=None):
        color   = _color(value, w, d)
        display = f"{value:.1f} {unit}" if value is not None else "N/A"
        return (
            f'<div class="info-card">'
            f'<div class="label">{label}</div>'
            f'<div class="value" style="color:{color}">{display}</div>'
            f'</div>'
        )

    a, b = st.columns(2)
    with a:
        st.markdown(_card("Temperature", temp, "°C",  35,  40),  unsafe_allow_html=True)
        st.markdown(_card("Gas",         gas,  "ppm", 300, 500), unsafe_allow_html=True)
    with b:
        st.markdown(_card("Humidity",    hum,  "%",   85,  None), unsafe_allow_html=True)
        st.markdown(_card("Vibration",   vib,  "g",   1.5, 2.5), unsafe_allow_html=True)

st.markdown("---")

# ── Section 2: Safety Compliance % (last 24h) ─────────────────────────────────
st.markdown("## 📈 Real-time Safety Compliance % (Last 24 Hours)")

if readings:
    df = pd.DataFrame(readings)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Rolling compliance % over time
    df = df.sort_values("timestamp")
    df["safe_int"]      = df["is_safe"].astype(int)
    df["compliance_pct"] = df["safe_int"].rolling(window=10, min_periods=1).mean() * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["compliance_pct"],
        mode="lines",
        fill="tozeroy",
        line=dict(color=COLORS["safe"], width=2),
        fillcolor="rgba(63,185,80,0.1)",
        name="Safety Compliance %",
    ))
    fig.add_hline(
        y=70,
        line=dict(color=COLORS["warning"], dash="dash", width=1),
        annotation_text="70% target",
        annotation_font_color=COLORS["warning"],
    )
    _layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("yaxis", "xaxis")}
    fig.update_layout(
        **_layout,
        height=280,
        yaxis=dict(**PLOTLY_LAYOUT["yaxis"], range=[0, 105], title="Compliance %"),
        xaxis=dict(**PLOTLY_LAYOUT["xaxis"], title="Time"),
    )
    current_pct = df["compliance_pct"].iloc[-1] if not df.empty else 0
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Current rolling compliance: **{current_pct:.1f}%** (10-reading window)")
else:
    st.info("No readings yet — waiting for data from the edge device.")

st.markdown("---")

# ── Section 3: Sensor trends ──────────────────────────────────────────────────
st.markdown("## 🌡️ Sensor Trends")

if readings:
    tab1, tab2, tab3, tab4 = st.tabs(["🌡 Temperature", "💧 Humidity", "💨 Gas (PPM)", "📳 Vibration"])

    def _trend(tab, col, label, color, warn, danger, yrange=None):
        with tab:
            if col not in df.columns or df[col].isna().all():
                st.info(f"No {label} data yet.")
                return
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["timestamp"], y=df[col],
                mode="lines+markers",
                line=dict(color=color, width=2),
                marker=dict(size=4),
                name=label,
                fill="tozeroy",
                fillcolor=color + "1a",
            ))
            if warn:
                fig.add_hline(y=warn,   line=dict(color=COLORS["warning"], dash="dash", width=1),
                              annotation_text="warn",  annotation_font_color=COLORS["warning"])
            if danger:
                fig.add_hline(y=danger, line=dict(color=COLORS["danger"],  dash="dash", width=1),
                              annotation_text="danger", annotation_font_color=COLORS["danger"])
            _base = {k: v for k, v in PLOTLY_LAYOUT.items() if k != "yaxis"}
            layout = dict(**_base, height=260,
                          yaxis=dict(**PLOTLY_LAYOUT["yaxis"], title=label))
            if yrange:
                layout["yaxis"]["range"] = yrange
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)

    _trend(tab1, "temperature_c", "Temperature (°C)", COLORS["orange"],  35, 40)
    _trend(tab2, "humidity_pct",  "Humidity (%)",     COLORS["cyan"],    85, None, [0, 100])
    _trend(tab3, "gas_ppm",       "Gas (PPM)",        COLORS["purple"],  300, 500)
    _trend(tab4, "vibration_g",   "Vibration (g)",    COLORS["blue"],    1.5, 2.5)

st.markdown("---")

# ── Section 4: Recent alert history ──────────────────────────────────────────
st.markdown("## 🚨 Recent Unsafe Events")

unsafe_rows = [r for r in readings if not r.get("is_safe", True)]
if unsafe_rows:
    df_alerts = pd.DataFrame(unsafe_rows)[
        ["timestamp", "alert_level", "alert_reasons", "temperature_c", "gas_ppm", "vibration_g", "helmet_detected", "vest_detected"]
    ].tail(15).iloc[::-1]
    df_alerts.columns = ["Time", "Level", "Reasons", "Temp °C", "Gas PPM", "Vib g", "Helmet", "Vest"]
    st.dataframe(df_alerts, use_container_width=True, hide_index=True)
    st.caption(f"Showing last 15 of {len(unsafe_rows)} unsafe events.")
else:
    st.success("No unsafe events in the current data window.")

st.markdown("---")

# ── Section 5: Quick controls ─────────────────────────────────────────────────
st.markdown("## 🎛️ Quick Controls")
st.markdown("Use the full **Control Panel** for threshold configuration and simulation.")

btn1, btn2, btn3, btn4 = st.columns(4)

with btn1:
    if st.button("🛑 Emergency Stop", use_container_width=True, type="primary"):
        ok = send_command("EMERGENCY_STOP")
        st.error("Emergency Stop sent.") if ok else st.error("Failed.")

with btn2:
    if st.button("🔄 Remote Reset", use_container_width=True):
        ok = send_command("RESET_SAFE")
        st.success("Reset sent.") if ok else st.error("Failed.")

with btn3:
    if st.button("📸 Capture Frame", use_container_width=True):
        ok = send_command("CAPTURE_FRAME")
        st.success("Capture queued.") if ok else st.error("Failed.")

with btn4:
    if st.button("⚙️ Threshold Adjuster →", use_container_width=True):
        st.switch_page("pages/5_Control.py")
