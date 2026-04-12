"""
Alert Log page – filterable history of unsafe events.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from utils.api_client import health_check, get_latest_readings
from utils.styles import CUSTOM_CSS, COLORS, PLOTLY_LAYOUT

st.set_page_config(page_title="Alert Log — Safety Monitor", page_icon="🚨", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st_autorefresh(interval=5_000, key="alerts_refresh")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Safety Monitor")
    st.markdown("---")
    st.page_link("app.py",                label="🏠 Live Overview")
    st.page_link("pages/1_Analytics.py",  label="📈 Analytics")
    st.page_link("pages/2_Alerts.py",     label="🚨 Alert Log")
    st.page_link("pages/3_Control.py",    label="🎛️  Control Panel")
    st.markdown("---")
    limit = st.select_slider("Data window", options=[30, 60, 120, 200], value=120)
    level_filter = st.multiselect(
        "Filter by level",
        options=["SAFE", "WARNING", "DANGER"],
        default=["WARNING", "DANGER"],
    )
    online = health_check()
    status_txt = "online" if online else "offline"
    color_cls  = "conn-online" if online else "conn-offline"
    st.markdown(f'<span class="{color_cls}">● Backend {status_txt}</span>', unsafe_allow_html=True)
    st.markdown(f"*{datetime.now().strftime('%H:%M:%S')}*")

st.markdown("# 🚨 Alert Log")
st.markdown("Filterable history of safety events.")

if not online:
    st.error("Backend offline.")
    st.stop()

readings = get_latest_readings(limit=limit)
if not readings:
    st.info("No data available yet.")
    st.stop()

df = pd.DataFrame(readings)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# ── KPI row ──────────────────────────────────────────────────────────────────
total   = len(df)
dangers = (df["alert_level"] == "DANGER").sum()  if "alert_level" in df else 0
warnings= (df["alert_level"] == "WARNING").sum() if "alert_level" in df else 0
unsafe  = (~df["is_safe"]).sum()                  if "is_safe"     in df else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Readings",  total)
c2.metric("DANGER Events",   int(dangers),  delta=None)
c3.metric("WARNING Events",  int(warnings), delta=None)
c4.metric("Unsafe Total",    int(unsafe))

st.markdown("---")

# ── Alert frequency bar chart ────────────────────────────────────────────────
st.markdown("## Alert Frequency Over Time")
if "alert_level" in df.columns:
    df_time = df.set_index("timestamp").resample("5min")["alert_level"].apply(
        lambda s: (s == "DANGER").sum() + (s == "WARNING").sum()
    ).reset_index()
    df_time.columns = ["Time", "Alert Count"]

    fig_freq = go.Figure(go.Bar(
        x=df_time["Time"], y=df_time["Alert Count"],
        marker_color=COLORS["danger"],
        name="Alerts per 5 min",
    ))
    fig_freq.update_layout(**{
        **PLOTLY_LAYOUT,
        "height": 240,
        "title": "Alerts per 5-minute Bucket",
        "xaxis": dict(**PLOTLY_LAYOUT["xaxis"], title="Time"),
        "yaxis": dict(**PLOTLY_LAYOUT["yaxis"], title="Count"),
    })
    st.plotly_chart(fig_freq, use_container_width=True)

st.markdown("---")

# ── Filtered alert table ─────────────────────────────────────────────────────
st.markdown("## Event Table")

df_filtered = df.copy()
if level_filter and "alert_level" in df.columns:
    df_filtered = df_filtered[df_filtered["alert_level"].isin(level_filter)]

display_cols = [c for c in [
    "timestamp", "alert_level", "alert_reasons",
    "temperature_c", "humidity_pct", "gas_ppm", "vibration_g",
    "helmet_detected", "vest_detected",
] if c in df_filtered.columns]

df_display = df_filtered[display_cols].iloc[::-1].copy()
df_display.columns = [c.replace("_", " ").title() for c in display_cols]

if df_display.empty:
    st.success("No events matching the selected filters.")
else:
    st.markdown(f"*{len(df_display)} events shown*")
    st.dataframe(df_display, use_container_width=True, hide_index=True, height=420)

    # Export
    csv = df_display.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Download as CSV",
        data=csv,
        file_name=f"safety_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )

st.markdown("---")

# ── Alert reasons breakdown ───────────────────────────────────────────────────
st.markdown("## Alert Reasons Breakdown")

unsafe_df = df[~df.get("is_safe", pd.Series([True]*len(df))).astype(bool)]
if not unsafe_df.empty and "alert_reasons" in unsafe_df.columns:
    from collections import Counter
    import ast

    reasons_flat = []
    for reasons_raw in unsafe_df["alert_reasons"].dropna():
        try:
            reasons = ast.literal_eval(reasons_raw) if isinstance(reasons_raw, str) else reasons_raw
            if isinstance(reasons, list):
                reasons_flat.extend(reasons)
        except Exception:
            reasons_flat.append(str(reasons_raw))

    if reasons_flat:
        counts = Counter(reasons_flat)
        df_reasons = pd.DataFrame(counts.items(), columns=["Reason", "Count"]).sort_values("Count", ascending=True)
        fig_h = px.bar(df_reasons, x="Count", y="Reason", orientation="h",
                       color="Count", color_continuous_scale=["#238636", "#d29922", "#da3633"])
        fig_h.update_layout(**{
            **PLOTLY_LAYOUT,
            "height": max(180, len(df_reasons) * 40),
            "showlegend": False,
            "coloraxis_showscale": False,
            "margin": dict(l=160, r=20, t=20, b=30),
        })
        st.plotly_chart(fig_h, use_container_width=True)
    else:
        st.info("No alert reason details found in this window.")
else:
    st.info("No unsafe events in the current window.")
