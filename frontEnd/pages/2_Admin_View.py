"""
Admin / Manager View — full dashboard: KPIs, live feed, PPE, sensors,
compliance chart, alert history, and quick controls.
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
    layout="wide",
    initial_sidebar_state="expanded",
)
require_admin()
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st_autorefresh(interval=3_000, key="admin_refresh")

# ── Sidebar ───────────────────────────────────────────────────────────────────
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

# ── Data ──────────────────────────────────────────────────────────────────────
if not online:
    st.error("Backend offline. Start with `uvicorn cloud.app:app --reload`.")
    st.stop()

stats       = get_stats() or {}
readings    = get_latest_readings(limit=200)
latest      = readings[-1] if readings else {}
frame       = get_latest_frame()
alert_frame = get_alert_frame()

status     = stats.get("current_status", latest.get("alert_level", "UNKNOWN"))
is_safe    = status == "SAFE"
is_danger  = status == "DANGER"
is_warning = status == "WARNING"
helmet_ok  = latest.get("helmet_detected", None)
vest_ok    = latest.get("vest_detected",   None)
violations = sum([helmet_ok is False, vest_ok is False])

temp = latest.get("temperature_c")
hum  = latest.get("humidity_pct")
gas  = latest.get("gas_ppm")
vib  = latest.get("vibration_g")

# ── Page header ───────────────────────────────────────────────────────────────
health_label = "Online" if online else "Offline"
health_color = COLORS["safe"] if online else COLORS["danger"]
st.markdown(
    f'<div class="factory-header">'
    f'<span class="fh-item"><strong>LOCATION</strong> Plant A, Building 3</span>'
    f'<span class="fh-item"><strong>DEVICE HEALTH</strong> <span style="color:{health_color};">{health_label}</span></span>'
    f'<span class="fh-item"><strong>LAST SYNC</strong> {datetime.now().strftime("%H:%M:%S")}</span>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<h1 style="margin-bottom:2px;">Admin Dashboard</h1>'
    '<p style="color:#8fa3c0;font-size:0.88rem;margin-bottom:0;">Full system overview — live feed, compliance, history &amp; controls</p>',
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

# ── KPI row ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Readings",  f"{stats.get('total_readings', 0):,}")
c2.metric("Unsafe Events",   f"{stats.get('unsafe_count', 0):,}")
c3.metric("Safe Rate",       f"{stats.get('safe_pct', 0.0):.1f}%")
c4.metric("Temperature",     f"{temp:.1f} °C" if temp is not None else "--")
c5.metric("Humidity",        f"{hum:.1f}%" if hum is not None else "--")

# ── Section: Camera + PPE ─────────────────────────────────────────────────────
st.markdown("""
<div class="section-head">
    <span class="section-head-text">Camera &amp; PPE Status</span>
    <span class="section-head-line"></span>
</div>
""", unsafe_allow_html=True)

cam_col, ppe_col = st.columns([3, 2], gap="large")

with cam_col:
    if is_danger or is_warning:
        st.markdown('<div class="cam-badge-alert"><span class="cam-dot"></span>VIOLATION IN PROGRESS</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="cam-badge-live"><span class="cam-dot"></span>LIVE</div>', unsafe_allow_html=True)

    wrap_cls = "cam-wrap-safe" if is_safe else ("cam-wrap-danger" if (is_danger or is_warning) else "cam-wrap-neutral")

    if os.environ.get("DASHBOARD_MODE", "LOCAL") == "CLOUD":
        st.markdown(
            '<div class="cam-placeholder">'
            '<strong>Live Feed Disabled (Cloud Mode)</strong>'
            'Monitoring via high-level telemetry and violation snapshots only.</div>',
            unsafe_allow_html=True,
        )
    elif frame:
        st.markdown(f'<div class="{wrap_cls}">', unsafe_allow_html=True)
        st.image(frame, caption="Live feed — bounding boxes show PPE detection", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="cam-placeholder">'
            '<strong>Camera feed unavailable</strong>'
            'Waiting for edge device…</div>',
            unsafe_allow_html=True,
        )

    viol_cls = "viol-count viol-danger" if violations > 0 else "viol-count viol-safe"
    viol_msg  = f"PPE Violations Active: {violations}" if violations > 0 else "All PPE Compliant"
    st.markdown(f'<div class="{viol_cls}">{viol_msg}</div>', unsafe_allow_html=True)

    if alert_frame:
        st.markdown('<hr/>', unsafe_allow_html=True)
        st.markdown('<h4 style="margin-bottom:10px;color:#f87171;">Latest Violation Capture</h4>', unsafe_allow_html=True)
        st.markdown(
            '<div style="background:rgba(248,113,113,0.06);border:1px solid rgba(248,113,113,0.2);'
            'border-radius:10px;padding:10px 14px;margin-bottom:12px;color:#fca5a5;font-size:0.82rem;">'
            'Captured at moment of PPE violation — review and take action.'
            '</div>',
            unsafe_allow_html=True,
        )
        st.image(alert_frame, caption="Violation capture", use_container_width=True)

with ppe_col:
    st.markdown('<h4 style="margin-bottom:12px;">PPE Compliance</h4>', unsafe_allow_html=True)

    def _ppe_card(name, detected):
        if detected is None:
            card_cls, ind_cls, ind_text, state_cls, state_text = \
                "ppe-card ppe-unknown", "ppe-indicator ppe-ind-unknown", "?", "ppe-state-unknown", "No data"
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

    st.markdown('<h4 style="margin:18px 0 12px;">Sensor Snapshot</h4>', unsafe_allow_html=True)

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

    def _detection_card(label, detected):
        color   = COLORS["danger"] if detected else COLORS["safe"]
        display = "DETECTED" if detected else "NORMAL"
        return (
            f'<div class="info-card">'
            f'<div class="label">{label}</div>'
            f'<div class="value" style="color:{color}">{display}</div>'
            f'</div>'
        )

    admin_reasons = latest.get("alert_reasons", [])
    gas_detected  = "gas_detected" in admin_reasons
    vib_detected  = "vibration_detected" in admin_reasons

    a, b = st.columns(2)
    with a:
        st.markdown(_card("Temperature", temp, "°C", 35, 40),    unsafe_allow_html=True)
        st.markdown(_detection_card("Gas", gas_detected),         unsafe_allow_html=True)
    with b:
        st.markdown(_card("Humidity", hum, "%", 85, None),        unsafe_allow_html=True)
        st.markdown(_detection_card("Vibration", vib_detected),   unsafe_allow_html=True)

# ── Section: Compliance Chart ─────────────────────────────────────────────────
st.markdown("""
<div class="section-head">
    <span class="section-head-text">Safety Compliance Trend</span>
    <span class="section-head-line"></span>
</div>
""", unsafe_allow_html=True)

if readings:
    df = pd.DataFrame(readings)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    df["safe_int"]       = df["is_safe"].astype(int)
    df["compliance_pct"] = df["safe_int"].rolling(window=10, min_periods=1).mean() * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["compliance_pct"],
        mode="lines",
        fill="tozeroy",
        line=dict(color=COLORS["safe"], width=2.5),
        fillcolor="rgba(52,211,153,0.08)",
        name="Safety Compliance %",
    ))
    fig.add_hline(
        y=70,
        line=dict(color=COLORS["warning"], dash="dot", width=1.5),
        annotation_text="70% target",
        annotation_font_color=COLORS["warning"],
    )
    _layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("yaxis", "xaxis")}
    fig.update_layout(
        **_layout,
        height=260,
        yaxis=dict(**PLOTLY_LAYOUT["yaxis"], range=[0, 105], title="Compliance %"),
        xaxis=dict(**PLOTLY_LAYOUT["xaxis"], title="Time"),
    )
    current_pct = df["compliance_pct"].iloc[-1] if not df.empty else 0
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Rolling 10-reading compliance: **{current_pct:.1f}%**")
else:
    st.info("No readings yet — waiting for data from the edge device.")

# ── Section: Sensor Trends ────────────────────────────────────────────────────
if readings:
    st.markdown("""
    <div class="section-head">
        <span class="section-head-text">Sensor Trends</span>
        <span class="section-head-line"></span>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Temperature", "Humidity", "Gas (PPM)", "Vibration"])

    def _trend(tab, col, label, color, warn, danger, yrange=None):
        with tab:
            if col not in df.columns or df[col].isna().all():
                st.info(f"No {label} data yet.")
                return
            fig = go.Figure()
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            fig.add_trace(go.Scatter(
                x=df["timestamp"], y=df[col],
                mode="lines+markers",
                line=dict(color=color, width=2.5),
                marker=dict(size=4),
                name=label,
                fill="tozeroy",
                fillcolor=f"rgba({r},{g},{b},0.09)",
            ))
            if warn:
                fig.add_hline(y=warn,   line=dict(color=COLORS["warning"], dash="dot", width=1.5),
                              annotation_text="warn",  annotation_font_color=COLORS["warning"])
            if danger:
                fig.add_hline(y=danger, line=dict(color=COLORS["danger"],  dash="dot", width=1.5),
                              annotation_text="danger", annotation_font_color=COLORS["danger"])
            _base = {k: v for k, v in PLOTLY_LAYOUT.items() if k != "yaxis"}
            layout = dict(**_base, height=260, yaxis=dict(**PLOTLY_LAYOUT["yaxis"], title=label))
            if yrange:
                layout["yaxis"]["range"] = yrange
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)

    _trend(tab1, "temperature_c", "Temperature (°C)", COLORS["orange"],  35,  40)
    _trend(tab2, "humidity_pct",  "Humidity (%)",     COLORS["cyan"],    85,  None, [0, 100])
    with tab3:
        st.info("Gas sensor provides detection only — numeric PPM measurement not available.")
    with tab4:
        st.info("Vibration sensor provides detection only — numeric g value not available.")

# ── Section: Recent Unsafe Events ─────────────────────────────────────────────
st.markdown("""
<div class="section-head">
    <span class="section-head-text">Recent Unsafe Events</span>
    <span class="section-head-line"></span>
</div>
""", unsafe_allow_html=True)

unsafe_rows = [r for r in readings if not r.get("is_safe", True)]
if unsafe_rows:
    df_alerts = pd.DataFrame(unsafe_rows)[
        ["timestamp", "alert_level", "alert_reasons",
         "temperature_c", "gas_ppm", "vibration_g", "helmet_detected", "vest_detected"]
    ].tail(15).iloc[::-1]
    df_alerts.columns = ["Time", "Level", "Reasons", "Temp °C", "Gas PPM", "Vib g", "Helmet", "Vest"]
    st.dataframe(df_alerts, use_container_width=True, hide_index=True)
    st.caption(f"Showing last 15 of {len(unsafe_rows)} unsafe events.")
else:
    st.success("No unsafe events in the current data window.")

# ── Section: Quick Controls ───────────────────────────────────────────────────
st.markdown("""
<div class="section-head">
    <span class="section-head-text">Quick Controls</span>
    <span class="section-head-line"></span>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<p style="font-size:0.85rem;color:#8fa3c0;margin-bottom:16px;">'
    'Use the full <strong>Control Panel</strong> for threshold configuration and simulation.</p>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div style="background:rgba(248,113,113,0.06);border:1px solid rgba(248,113,113,0.2);'
    'border-left:4px solid #f87171;border-radius:12px;padding:14px 20px;margin-bottom:18px;">'
    '<span style="color:#f87171;font-size:0.9rem;font-weight:700;">Emergency Stop</span>'
    '<span style="color:#8b949e;font-size:0.9rem;"> — halts all inference on the edge device</span>'
    '</div>',
    unsafe_allow_html=True,
)

btn1, btn2, btn3, btn4 = st.columns(4)
with btn1:
    if st.button("Emergency Stop", use_container_width=True, type="primary"):
        ok = send_command("EMERGENCY_STOP")
        st.error("Emergency Stop sent.") if ok else st.error("Failed.")
with btn2:
    if st.button("Remote Reset", use_container_width=True):
        ok = send_command("RESET_SAFE")
        st.success("Reset sent.") if ok else st.error("Failed.")
with btn3:
    if st.button("Capture Frame", use_container_width=True):
        ok = send_command("CAPTURE_FRAME")
        st.success("Capture queued.") if ok else st.error("Failed.")
with btn4:
    if st.button("Threshold Adjuster", use_container_width=True):
        st.switch_page("pages/5_Control.py")
