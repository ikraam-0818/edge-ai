"""
Custom CSS injected into every Streamlit page.
Defines the dark, industrial safety theme.
"""

CUSTOM_CSS = """
<style>
/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: 'Segoe UI', system-ui, sans-serif;
}

[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}

/* Hide Streamlit's auto-generated page navigation */
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] {
    display: none !important;
}

/* ── Headers ── */
h1 { color: #58a6ff; font-weight: 700; letter-spacing: -0.5px; }
h2 { color: #8b949e; font-weight: 600; }
h3 { color: #c9d1d9; font-weight: 600; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px 20px;
}
[data-testid="metric-container"] label {
    color: #8b949e !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #e6edf3 !important;
}

/* ── Status banner ── */
.status-safe {
    background: linear-gradient(135deg, #0d2818, #1a472a);
    border: 1px solid #238636;
    border-radius: 12px;
    padding: 20px 28px;
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    color: #3fb950;
    letter-spacing: 0.1em;
    margin-bottom: 16px;
}
.status-warning {
    background: linear-gradient(135deg, #2d1f00, #3d2b00);
    border: 1px solid #d29922;
    border-radius: 12px;
    padding: 20px 28px;
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    color: #e3b341;
    letter-spacing: 0.1em;
    margin-bottom: 16px;
}
.status-danger {
    background: linear-gradient(135deg, #2d0f0f, #4a1515);
    border: 1px solid #da3633;
    border-radius: 12px;
    padding: 20px 28px;
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    color: #f85149;
    letter-spacing: 0.1em;
    animation: pulse-red 1.5s infinite;
    margin-bottom: 16px;
}
@keyframes pulse-red {
    0%, 100% { border-color: #da3633; }
    50%       { border-color: #f85149; }
}

/* ── Info card ── */
.info-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 12px;
}
.info-card .label {
    color: #8b949e;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
}
.info-card .value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #e6edf3;
}

/* ── Connection pill ── */
.conn-online  { color: #3fb950; font-weight: 600; }
.conn-offline { color: #f85149; font-weight: 600; }

/* ── Divider ── */
hr { border-color: #30363d; }

/* ── Scrollable table ── */
[data-testid="stDataFrame"] {
    border: 1px solid #30363d;
    border-radius: 8px;
}

/* ── Buttons ── */
button[kind="primary"] {
    background-color: #238636 !important;
    border-color: #2ea043 !important;
}
button[kind="secondary"] {
    background-color: #21262d !important;
    border-color: #30363d !important;
    color: #c9d1d9 !important;
}
</style>
"""


# Colour palette used in Plotly charts
COLORS = {
    "safe":       "#3fb950",
    "warning":    "#e3b341",
    "danger":     "#f85149",
    "blue":       "#58a6ff",
    "purple":     "#a371f7",
    "cyan":       "#39d3bb",
    "orange":     "#f0883e",
    "grid":       "#21262d",
    "background": "#0d1117",
    "paper":      "#161b22",
    "text":       "#e6edf3",
    "subtext":    "#8b949e",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor=COLORS["paper"],
    plot_bgcolor =COLORS["background"],
    font         =dict(color=COLORS["text"], size=12),
    xaxis        =dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"]),
    yaxis        =dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"]),
    margin       =dict(l=50, r=20, t=40, b=40),
    legend       =dict(bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS["subtext"])),
)
