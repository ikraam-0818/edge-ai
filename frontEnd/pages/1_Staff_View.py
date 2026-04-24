"""
Staff / Worker View — live camera, PPE compliance, environmental sensors.
Workers see only what they need: current safety status, PPE, and sensor readings.
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
from utils.auth import require_login, sidebar_user_info, current_role, ROLE_ADMIN

st.set_page_config(
    page_title="Staff View — Safety Monitor",
    layout="wide",
    initial_sidebar_state="expanded",
)
require_login()
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st_autorefresh(interval=3_000, key="staff_refresh")

# ── Sidebar — workers only see Staff View ─────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:4px 0 16px;">
        <div style="font-weight:800;font-size:0.95rem;color:#e8edf5;letter-spacing:-0.3px;">Safety Monitor</div>
        <div style="font-size:0.7rem;color:#4a6080;font-weight:600;">Edge AI System</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<div style="font-size:0.65rem;font-weight:700;color:#4a6080;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:8px;">Navigation</div>', unsafe_allow_html=True)
    st.page_link("pages/1_Staff_View.py", label="Live View")
    if current_role() == ROLE_ADMIN:
        st.page_link("pages/2_Admin_View.py", label="Admin Dashboard")
        st.page_link("pages/3_Analytics.py",  label="Analytics")
        st.page_link("pages/4_Alerts.py",     label="Alert Log")
        st.page_link("pages/5_Control.py",    label="Control Panel")

    st.markdown("---")
    sidebar_user_info()

    online = health_check()
    conn_cls = "conn-online" if online else "conn-offline"
    conn_dot = "conn-dot-on" if online else ""
    st.markdown(
        f'<div class="{conn_cls}"><span class="conn-dot {conn_dot}"></span>'
        f'Backend {"online" if online else "offline"}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="font-size:0.72rem;color:#4a6080;margin-top:6px;">'
        f'Updated {datetime.now().strftime("%H:%M:%S")}</div>',
        unsafe_allow_html=True,
    )

# ── Fetch data ────────────────────────────────────────────────────────────────
if not online:
    st.error("Backend offline. Contact your site administrator.")
    st.stop()

stats       = get_stats() or {}
readings    = get_latest_readings(limit=1)
latest      = readings[0] if readings else {}
live_frame  = get_latest_frame()
alert_frame = get_alert_frame()

status     = stats.get("current_status", latest.get("alert_level", "UNKNOWN"))
is_safe    = status == "SAFE"
is_danger  = status == "DANGER"
is_warning = status == "WARNING"

helmet_ok  = latest.get("helmet_detected", None)
vest_ok    = latest.get("vest_detected",   None)
violations = sum([helmet_ok is False, vest_ok is False])
reasons    = latest.get("alert_reasons", [])

temp = latest.get("temperature_c")
hum  = latest.get("humidity_pct")
gas  = latest.get("gas_ppm")
vib  = latest.get("vibration_g")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    '<h1 style="margin-bottom:2px;">Live Safety View</h1>'
    '<p style="color:#8fa3c0;font-size:0.88rem;margin-bottom:0;">Real-time PPE detection &amp; environmental monitoring</p>',
    unsafe_allow_html=True,
)

# ── Status banner ─────────────────────────────────────────────────────────────
css_map = {"SAFE": "status-safe", "WARNING": "status-warning", "DANGER": "status-danger"}
banner_cls = css_map.get(status, "status-warning")
st.markdown(
    f'<div class="{banner_cls}">'
    f'<span class="status-dot"></span>'
    f'<span class="status-text">SITE STATUS — {status}</span>'
    f'<span class="status-time">{datetime.now().strftime("%H:%M:%S")}</span>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Violation alert (only when PPE missing) ───────────────────────────────────
if not is_safe and violations > 0:
    items_html = ""
    if helmet_ok is False:
        items_html += '<div class="v-item"><span class="v-item-dot"></span>Safety Helmet — <strong>NOT detected</strong></div>'
    if vest_ok is False:
        items_html += '<div class="v-item"><span class="v-item-dot"></span>Safety Vest — <strong>NOT detected</strong></div>'
    st.markdown(
        f'<div class="violation-box">'
        f'<div class="v-title">PPE Violation Detected</div>'
        f'<div class="v-sub">Immediate action required — the following PPE items are missing:</div>'
        f'{items_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Main layout ───────────────────────────────────────────────────────────────
cam_col, info_col = st.columns([3, 2], gap="large")

# ── Camera column ─────────────────────────────────────────────────────────────
with cam_col:
    if is_danger or is_warning:
        st.markdown('<div class="cam-badge-alert"><span class="cam-dot"></span>VIOLATION IN PROGRESS</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="cam-badge-live"><span class="cam-dot"></span>LIVE</div>', unsafe_allow_html=True)

    st.markdown('<h4 style="margin-bottom:10px;">Live Camera Feed</h4>', unsafe_allow_html=True)

    wrap_cls = "cam-wrap-safe" if is_safe else ("cam-wrap-danger" if (is_danger or is_warning) else "cam-wrap-neutral")

    if os.environ.get("DASHBOARD_MODE", "LOCAL") == "CLOUD":
        st.markdown(
            '<div class="cam-placeholder">'
            '<strong>Live Feed Disabled in Cloud Mode</strong>'
            'Only critical violation snapshots are synced to save bandwidth.</div>',
            unsafe_allow_html=True,
        )
    elif live_frame:
        st.markdown(f'<div class="{wrap_cls}">', unsafe_allow_html=True)
        st.image(live_frame, caption="Live feed — bounding boxes show PPE detection", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="cam-placeholder">'
            '<strong>Camera feed unavailable</strong>'
            'Waiting for edge device to connect…</div>',
            unsafe_allow_html=True,
        )

    viol_cls = "viol-count viol-danger" if violations > 0 else "viol-count viol-safe"
    viol_msg  = f"PPE Violations Active: {violations}" if violations > 0 else "All PPE Compliant"
    st.markdown(f'<div class="{viol_cls}">{viol_msg}</div>', unsafe_allow_html=True)

    # Latest violation capture
    if alert_frame:
        st.markdown('<hr/>', unsafe_allow_html=True)
        st.markdown('<h4 style="margin-bottom:10px;color:#f87171;">Latest Violation Capture</h4>', unsafe_allow_html=True)
        st.markdown(
            '<div style="background:rgba(248,113,113,0.06);border:1px solid rgba(248,113,113,0.2);'
            'border-radius:10px;padding:10px 14px;margin-bottom:12px;color:#fca5a5;font-size:0.82rem;">'
            'Captured at the moment of PPE violation — review and take corrective action.'
            '</div>',
            unsafe_allow_html=True,
        )
        st.image(alert_frame, caption="Violation capture", use_container_width=True)

# ── Info column: PPE + Sensors ────────────────────────────────────────────────
with info_col:

    # PPE compliance
    st.markdown('<h4 style="margin-bottom:12px;">PPE Compliance</h4>', unsafe_allow_html=True)

    def _ppe_card(name, detected):
        if detected is None:
            card_cls, ind_cls, ind_text, state_cls, state_text = \
                "ppe-card ppe-unknown", "ppe-indicator ppe-ind-unknown", "?", "ppe-state-unknown", "No data yet"
        elif detected:
            card_cls, ind_cls, ind_text, state_cls, state_text = \
                "ppe-card ppe-ok", "ppe-indicator ppe-ind-ok", "OK", "ppe-state-ok", "Detected"
        else:
            card_cls, ind_cls, ind_text, state_cls, state_text = \
                "ppe-card ppe-fail", "ppe-indicator ppe-ind-fail", "X", "ppe-state-fail", "NOT Detected"
        return (
            f'<div class="{card_cls}">'
            f'  <div class="{ind_cls}">{ind_text}</div>'
            f'  <div class="ppe-info">'
            f'    <div class="ppe-name">{name}</div>'
            f'    <div class="{state_cls}">{state_text}</div>'
            f'  </div>'
            f'</div>'
        )

    st.markdown(_ppe_card("Safety Helmet", helmet_ok), unsafe_allow_html=True)
    st.markdown(_ppe_card("Safety Vest",   vest_ok),   unsafe_allow_html=True)

    # Alert reasons
    if reasons:
        st.markdown('<h4 style="margin:16px 0 10px;">Active Alerts</h4>', unsafe_allow_html=True)
        for r in reasons:
            st.markdown(
                f'<div class="alert-reason">{r.replace("_"," ").title()}</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<hr style="margin:18px 0;"/>', unsafe_allow_html=True)

    # Environmental sensors with progress bars
    st.markdown('<h4 style="margin-bottom:12px;">Environmental Sensors</h4>', unsafe_allow_html=True)

    def _sensor_color(v, w, d):
        if v is None: return COLORS["subtext"]
        if d and v >= d: return COLORS["danger"]
        if w and v >= w: return COLORS["warning"]
        return COLORS["safe"]

    def _bar_pct(v, warn, danger):
        if v is None: return 0, COLORS["subtext"]
        limit  = (danger or warn or 1) * 1.2
        pct    = min(int(v / limit * 100), 100)
        color  = _sensor_color(v, warn, danger)
        return pct, color

    def _sensor_card(label, value, unit, warn=None, danger=None):
        color   = _sensor_color(value, warn, danger)
        display = f"{value:.1f} {unit}" if value is not None else "N/A"
        pct, bar_color = _bar_pct(value, warn, danger)
        thresh_txt = f"Warn at {warn}{unit}" if warn else ""
        return (
            f'<div class="sensor-card">'
            f'  <div class="s-label">{label}</div>'
            f'  <div class="s-value" style="color:{color}">{display}</div>'
            f'  <div class="s-bar-track"><div class="s-bar-fill" style="width:{pct}%;background:{bar_color};"></div></div>'
            f'  <div class="s-bar-label">{thresh_txt}</div>'
            f'</div>'
        )

    p1, p2 = st.columns(2)
    with p1:
        st.markdown(_sensor_card("Temperature", temp, "°C",  warn=35,  danger=40),  unsafe_allow_html=True)
        st.markdown(_sensor_card("Gas (PPM)",   gas,  " ppm", warn=300, danger=500), unsafe_allow_html=True)
    with p2:
        st.markdown(_sensor_card("Humidity",    hum,  "%",    warn=85),              unsafe_allow_html=True)
        st.markdown(_sensor_card("Vibration",   vib,  " g",   warn=1.5, danger=2.5), unsafe_allow_html=True)
