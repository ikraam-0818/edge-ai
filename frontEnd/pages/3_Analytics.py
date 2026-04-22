"""
Analytics page – historical sensor trends & PPE compliance metrics.
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
from utils.auth import require_admin, sidebar_user_info

st.set_page_config(page_title="Analytics — Safety Monitor", layout="wide")
require_admin()
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st_autorefresh(interval=5_000, key="analytics_refresh")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:4px 0 16px;">
        <img src="https://img.icons8.com/color/96/hard-hat.png" width="36"/>
        <div>
            <div style="font-weight:800;font-size:0.95rem;color:#e8edf5;letter-spacing:-0.3px;">Safety Monitor</div>
            <div style="font-size:0.7rem;color:#4a6080;font-weight:600;">Edge AI System</div>
        </div>
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
    limit = st.select_slider(
        "Data window (readings)",
        options=[30, 60, 90, 120, 200],
        value=120,
    )
    sidebar_user_info()
    online = health_check()
    conn_cls = "conn-online" if online else "conn-offline"
    conn_dot = "conn-dot-on" if online else ""
    st.markdown(
        f'<div class="{conn_cls}"><span class="conn-dot {conn_dot}"></span>'
        f'Backend {"online" if online else "offline"}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div style="font-size:0.72rem;color:#4a6080;margin-top:6px;">Updated {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)

st.markdown("# Analytics")
st.markdown("Historical sensor trends and PPE compliance metrics.")

if not online:
    st.error("Backend offline. Start with `uvicorn cloud.app:app --reload`.")
    st.stop()

readings = get_latest_readings(limit=limit)
if not readings:
    st.info("No data available yet.")
    st.stop()

df = pd.DataFrame(readings)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# ── Section 1 : PPE Compliance ────────────────────────────────────────────────
st.markdown("---")
st.markdown("## PPE Compliance")

col1, col2, col3 = st.columns(3)

helmet_rate = df["helmet_detected"].mean() * 100 if "helmet_detected" in df else 0
vest_rate   = df["vest_detected"].mean()   * 100 if "vest_detected"   in df else 0
safe_rate   = df["is_safe"].mean()         * 100 if "is_safe"         in df else 0

col1.metric("Helmet Compliance",  f"{helmet_rate:.1f}%")
col2.metric("Vest Compliance",    f"{vest_rate:.1f}%")
col3.metric("Overall Safe Rate",  f"{safe_rate:.1f}%")

# PPE time-series
fig_ppe = go.Figure()
fig_ppe.add_trace(go.Scatter(
    x=df["timestamp"], y=df["helmet_detected"].astype(int),
    name="Helmet detected", mode="lines",
    line=dict(color=COLORS["safe"], width=2),
))
fig_ppe.add_trace(go.Scatter(
    x=df["timestamp"], y=df["vest_detected"].astype(int),
    name="Vest detected", mode="lines",
    line=dict(color=COLORS["blue"], width=2, dash="dot"),
))
fig_ppe.add_trace(go.Scatter(
    x=df["timestamp"], y=(~df["is_safe"]).astype(int),
    name="Unsafe event", mode="markers",
    marker=dict(color=COLORS["danger"], size=8, symbol="x"),
))
fig_ppe.update_layout(
    **{k: v for k, v in PLOTLY_LAYOUT.items() if k != "yaxis"},
    height=260,
    title="PPE Detection & Safety Events Over Time",
    yaxis=dict(**PLOTLY_LAYOUT["yaxis"], tickvals=[0, 1], ticktext=["No", "Yes"]),
)
st.plotly_chart(fig_ppe, use_container_width=True)

# ── Section 2 : Environmental Sensors ────────────────────────────────────────
st.markdown("---")
st.markdown("## Environmental Sensors")

env_cols = ["temperature_c", "humidity_pct", "gas_ppm", "vibration_g"]
env_labels = {
    "temperature_c": ("Temperature (°C)", COLORS["orange"]),
    "humidity_pct":  ("Humidity (%)",     COLORS["cyan"]),
    "gas_ppm":       ("Gas (PPM)",        COLORS["purple"]),
    "vibration_g":   ("Vibration (g)",    COLORS["blue"]),
}
warn_levels  = {"temperature_c": 35, "humidity_pct": 85, "gas_ppm": 300, "vibration_g": 1.5}
danger_levels= {"temperature_c": 40, "gas_ppm": 500, "vibration_g": 2.5}

available = [c for c in env_cols if c in df.columns and not df[c].isna().all()]

if available:
    # Summary stats table
    stats_data = []
    for col in available:
        label, _ = env_labels[col]
        stats_data.append({
            "Sensor": label,
            "Min":    round(df[col].min(), 2),
            "Max":    round(df[col].max(), 2),
            "Mean":   round(df[col].mean(), 2),
            "Std":    round(df[col].std(), 2),
            "Latest": round(df[col].iloc[-1], 2) if not df[col].isna().iloc[-1] else "N/A",
        })
    st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

    # 2×2 subplot grid
    rows = [available[i:i+2] for i in range(0, len(available), 2)]
    for row_cols in rows:
        cols = st.columns(len(row_cols), gap="medium")
        for col_widget, sensor_col in zip(cols, row_cols):
            label, color = env_labels[sensor_col]
            with col_widget:
                fig = go.Figure()
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                fig.add_trace(go.Scatter(
                    x=df["timestamp"], y=df[sensor_col],
                    mode="lines+markers",
                    line=dict(color=color, width=2),
                    marker=dict(size=3),
                    name=label,
                    fill="tozeroy",
                    fillcolor=f"rgba({r},{g},{b},0.13)",
                ))
                if sensor_col in warn_levels:
                    fig.add_hline(y=warn_levels[sensor_col],
                                  line=dict(color=COLORS["warning"], dash="dash", width=1))
                if sensor_col in danger_levels:
                    fig.add_hline(y=danger_levels[sensor_col],
                                  line=dict(color=COLORS["danger"], dash="dash", width=1))
                fig.update_layout(**{
                    **PLOTLY_LAYOUT,
                    "height": 240,
                    "title": dict(text=label, font=dict(size=13, color=COLORS["subtext"])),
                    "showlegend": False,
                    "margin": dict(l=40, r=10, t=40, b=30),
                })
                st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No environmental sensor data in this window.")

# ── Section 3 : Alert Level Distribution ────────────────────────────────────
st.markdown("---")
st.markdown("## Alert Level Distribution")

if "alert_level" in df.columns:
    dist = df["alert_level"].value_counts().reset_index()
    dist.columns = ["Level", "Count"]
    color_map = {"SAFE": COLORS["safe"], "WARNING": COLORS["warning"], "DANGER": COLORS["danger"]}

    cl, cr = st.columns([1, 2])
    with cl:
        fig_pie = px.pie(
            dist, names="Level", values="Count",
            color="Level",
            color_discrete_map=color_map,
            hole=0.45,
        )
        fig_pie.update_layout(**{
            **PLOTLY_LAYOUT,
            "height": 280,
            "showlegend": True,
            "margin": dict(l=10, r=10, t=30, b=10),
        })
        st.plotly_chart(fig_pie, use_container_width=True)

    with cr:
        fig_bar = px.bar(
            dist, x="Level", y="Count",
            color="Level",
            color_discrete_map=color_map,
        )
        fig_bar.update_layout(**{
            **PLOTLY_LAYOUT,
            "height": 280,
            "showlegend": False,
            "margin": dict(l=40, r=10, t=30, b=30),
        })
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No alert level data available.")

# ── Section 4 : Correlation heatmap ─────────────────────────────────────────
st.markdown("---")
st.markdown("## Sensor Correlation")

numeric_cols = [c for c in env_cols if c in df.columns and not df[c].isna().all()]
if len(numeric_cols) >= 2:
    corr = df[numeric_cols].corr()
    labels = [env_labels[c][0] for c in numeric_cols]
    fig_heat = go.Figure(go.Heatmap(
        z=corr.values.tolist(),
        x=labels, y=labels,
        colorscale="RdBu",
        zmid=0,
        text=[[f"{v:.2f}" for v in row] for row in corr.values],
        texttemplate="%{text}",
        colorbar=dict(tickfont=dict(color=COLORS["subtext"])),
    ))
    fig_heat.update_layout(
        **PLOTLY_LAYOUT, height=320,
        title="Pearson Correlation Between Sensors",
    )
    st.plotly_chart(fig_heat, use_container_width=True)
