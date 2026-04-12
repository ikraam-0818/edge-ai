"""
Edge AI – Construction Safety Monitor
======================================
Home / Live Overview  (auto-refreshes every 3 s)

Run with:
    cd frontEnd
    streamlit run app.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from utils.api_client import health_check, get_stats, get_latest_readings
from utils.styles import CUSTOM_CSS, COLORS, PLOTLY_LAYOUT

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Safety Monitor — Live",
    page_icon="🦺",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── Auto-refresh every 3 s ───────────────────────────────────────────────────
st_autorefresh(interval=3_000, key="home_refresh")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://img.icons8.com/color/96/hard-hat.png",
        width=72,
    )
    st.markdown("## Safety Monitor")
    st.markdown("**Edge AI — Construction PPE**")
    st.markdown("---")
    st.markdown("**Navigation**")
    st.page_link("app.py",                label="🏠 Live Overview",  )
    st.page_link("pages/1_Analytics.py",  label="📈 Analytics"      )
    st.page_link("pages/2_Alerts.py",     label="🚨 Alert Log"       )
    st.page_link("pages/3_Control.py",    label="🎛️  Control Panel"  )
    st.markdown("---")

    # Connection status
    online = health_check()
    if online:
        st.markdown('<span class="conn-online">● Backend online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="conn-offline">● Backend offline</span>', unsafe_allow_html=True)

    st.markdown(f"*Last refresh: {datetime.now().strftime('%H:%M:%S')}*")

# ── Title ────────────────────────────────────────────────────────────────────
st.markdown("# 🦺 Construction Safety Monitor")
st.markdown("**Live Overview** — real-time PPE & environmental data from the edge device")

if not online:
    st.error(
        "Cannot reach the backend API at `http://localhost:8000`. "
        "Start the FastAPI server with `uvicorn cloud.main:app --reload` and refresh."
    )
    st.stop()

# ── Fetch data ───────────────────────────────────────────────────────────────
stats    = get_stats() or {}
readings = get_latest_readings(limit=60)
latest   = readings[-1] if readings else {}

# ── Status banner ────────────────────────────────────────────────────────────
alert_level = stats.get("current_status", latest.get("alert_level", "UNKNOWN"))
icons = {"SAFE": "✅", "WARNING": "⚠️", "DANGER": "🚨", "UNKNOWN": "❓"}
icon  = icons.get(alert_level, "❓")

css_class = {
    "SAFE":    "status-safe",
    "WARNING": "status-warning",
    "DANGER":  "status-danger",
}.get(alert_level, "status-warning")

st.markdown(
    f'<div class="{css_class}">{icon} &nbsp; SITE STATUS: {alert_level}</div>',
    unsafe_allow_html=True,
)

# ── Top KPI row ──────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

total_r = stats.get("total_readings", 0)
unsafe  = stats.get("unsafe_count", 0)
safe_p  = stats.get("safe_pct", 0.0)

c1.metric("Total Readings",   f"{total_r:,}")
c2.metric("Unsafe Events",    f"{unsafe:,}",   delta=None)
c3.metric("Safe Rate",        f"{safe_p:.1f}%")
c4.metric("Temperature",
          f"{latest.get('temperature_c', '--')} °C" if latest.get('temperature_c') is not None else "--")
c5.metric("Humidity",
          f"{latest.get('humidity_pct', '--')} %" if latest.get('humidity_pct') is not None else "--")

st.markdown("---")

# ── Two-column layout: gauges + sensor row ───────────────────────────────────
left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown("### PPE Compliance (last 60 readings)")

    if readings:
        df = pd.DataFrame(readings)
        helmet_rate = df["helmet_detected"].mean() * 100 if "helmet_detected" in df else 0
        vest_rate   = df["vest_detected"].mean()   * 100 if "vest_detected"   in df else 0
    else:
        helmet_rate = vest_rate = 0

    # Gauge – helmet compliance
    fig_gauge = go.Figure()
    for i, (label, val, col) in enumerate([
        ("Helmet %", helmet_rate, COLORS["safe"] if helmet_rate > 70 else COLORS["danger"]),
        ("Vest %",   vest_rate,   COLORS["safe"] if vest_rate   > 70 else COLORS["danger"]),
    ]):
        fig_gauge.add_trace(go.Indicator(
            mode  = "gauge+number",
            value = round(val, 1),
            title = {"text": label, "font": {"color": COLORS["subtext"], "size": 14}},
            number= {"suffix": "%", "font": {"color": COLORS["text"], "size": 28}},
            gauge = dict(
                axis        = dict(range=[0, 100], tickcolor=COLORS["subtext"]),
                bar         = dict(color=col),
                bgcolor     = COLORS["grid"],
                bordercolor = COLORS["paper"],
                steps=[
                    dict(range=[0, 50],  color="#2d0f0f"),
                    dict(range=[50, 75], color="#2d2000"),
                    dict(range=[75, 100],color="#0d2818"),
                ],
                threshold=dict(line=dict(color=COLORS["warning"], width=3), thickness=0.75, value=70),
            ),
            domain={"row": 0, "column": i},
        ))

    fig_gauge.update_layout(
        **PLOTLY_LAYOUT,
        grid={"rows": 1, "columns": 2},
        height=260,
        margin=dict(l=30, r=30, t=20, b=10),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with right:
    st.markdown("### Sensor Snapshot (last reading)")

    temp  = latest.get("temperature_c")
    hum   = latest.get("humidity_pct")
    gas   = latest.get("gas_ppm")
    vib   = latest.get("vibration_g")

    def _card(label: str, value, unit: str, warn_above=None, danger_above=None):
        if value is None:
            display = "N/A"
            color   = COLORS["subtext"]
        else:
            display = f"{value:.1f} {unit}"
            if danger_above and value >= danger_above:
                color = COLORS["danger"]
            elif warn_above and value >= warn_above:
                color = COLORS["warning"]
            else:
                color = COLORS["safe"]
        return (
            f'<div class="info-card">'
            f'  <div class="label">{label}</div>'
            f'  <div class="value" style="color:{color}">{display}</div>'
            f'</div>'
        )

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(_card("Temperature",  temp,  "°C",  warn_above=35, danger_above=40), unsafe_allow_html=True)
        st.markdown(_card("Gas (PPM)",    gas,   "ppm", warn_above=300, danger_above=500), unsafe_allow_html=True)
    with col_b:
        st.markdown(_card("Humidity",     hum,   "%",   warn_above=85), unsafe_allow_html=True)
        st.markdown(_card("Vibration",    vib,   "g",   warn_above=1.5, danger_above=2.5), unsafe_allow_html=True)

st.markdown("---")

# ── Trend line (last 60 readings) ────────────────────────────────────────────
st.markdown("### Live Sensor Trends (last 60 readings)")

if readings:
    df = pd.DataFrame(readings)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

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
                fillcolor=color.replace(")", ",0.1)").replace("rgb", "rgba") if color.startswith("rgb") else color + "1a",
            ))
            if warn:
                fig.add_hline(y=warn,   line=dict(color=COLORS["warning"], dash="dash", width=1),
                              annotation_text="warn",  annotation_font_color=COLORS["warning"])
            if danger:
                fig.add_hline(y=danger, line=dict(color=COLORS["danger"],  dash="dash", width=1),
                              annotation_text="danger", annotation_font_color=COLORS["danger"])
            layout = dict(**PLOTLY_LAYOUT, height=280,
                          yaxis=dict(**PLOTLY_LAYOUT["yaxis"], title=label))
            if yrange:
                layout["yaxis"]["range"] = yrange
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)

    _trend(tab1, "temperature_c", "Temperature (°C)", COLORS["orange"],  35, 40)
    _trend(tab2, "humidity_pct",  "Humidity (%)",     COLORS["cyan"],    85, None, [0, 100])
    _trend(tab3, "gas_ppm",       "Gas (PPM)",        COLORS["purple"],  300, 500)
    _trend(tab4, "vibration_g",   "Vibration (g)",    COLORS["blue"],    1.5, 2.5)
else:
    st.info("No readings available yet. Waiting for data from the edge device.")

# ── Recent alert reasons ──────────────────────────────────────────────────────
unsafe_rows = [r for r in readings if not r.get("is_safe", True)]
if unsafe_rows:
    st.markdown("---")
    st.markdown("### Recent Unsafe Events")
    df_alerts = pd.DataFrame(unsafe_rows)[
        ["timestamp", "alert_level", "alert_reasons", "temperature_c", "gas_ppm", "vibration_g"]
    ].tail(10).iloc[::-1]
    df_alerts.columns = ["Time", "Level", "Reasons", "Temp °C", "Gas PPM", "Vib g"]
    st.dataframe(df_alerts, use_container_width=True, hide_index=True)
