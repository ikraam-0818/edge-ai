"""
Design system — dark industrial safety theme.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Design tokens ── */
:root {
  --bg:      #080c14;
  --surface: #0c1220;
  --card:    #101828;
  --card-2:  #141f30;
  --border:  rgba(255,255,255,0.07);
  --border-h: rgba(255,255,255,0.12);

  --blue:    #4d8ef7;
  --blue-bg: rgba(77,142,247,0.1);
  --green:   #34d399;
  --green-bg: rgba(52,211,153,0.1);
  --yellow:  #fbbf24;
  --yellow-bg: rgba(251,191,36,0.1);
  --red:     #f87171;
  --red-bg:  rgba(248,113,113,0.1);
  --orange:  #fb923c;
  --cyan:    #22d3ee;
  --purple:  #a78bfa;

  --text:    #e8edf5;
  --text-sub: #8fa3c0;
  --text-muted: #4a6080;

  --radius:    12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
}
.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 2rem !important;
    max-width: 1440px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] { display: none !important; }

/* ── Typography ── */
h1 {
    color: var(--text) !important;
    font-size: 1.65rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.6px !important;
    line-height: 1.2 !important;
}
h2 {
    color: var(--text-sub) !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
}
h3 {
    color: var(--text) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
}
h4 {
    color: var(--text-sub) !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 18px 22px !important;
    transition: border-color 0.2s, background 0.2s;
}
[data-testid="metric-container"]:hover {
    border-color: var(--border-h) !important;
    background: var(--card-2) !important;
}
[data-testid="metric-container"] label {
    color: var(--text-muted) !important;
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    color: var(--text) !important;
    letter-spacing: -0.5px !important;
}

/* ── Status banners ── */
.status-safe {
    background: var(--green-bg);
    border: 1px solid rgba(52,211,153,0.28);
    border-left: 4px solid var(--green);
    border-radius: var(--radius);
    padding: 16px 22px;
    margin-bottom: 20px;
    font-weight: 700;
    font-size: 1.05rem;
    color: var(--green);
    letter-spacing: 0.04em;
    display: flex;
    align-items: center;
    gap: 12px;
}
.status-warning {
    background: var(--yellow-bg);
    border: 1px solid rgba(251,191,36,0.28);
    border-left: 4px solid var(--yellow);
    border-radius: var(--radius);
    padding: 16px 22px;
    margin-bottom: 20px;
    font-weight: 700;
    font-size: 1.05rem;
    color: var(--yellow);
    letter-spacing: 0.04em;
    display: flex;
    align-items: center;
    gap: 12px;
}
.status-danger {
    background: var(--red-bg);
    border: 1px solid rgba(248,113,113,0.35);
    border-left: 4px solid var(--red);
    border-radius: var(--radius);
    padding: 16px 22px;
    margin-bottom: 20px;
    font-weight: 700;
    font-size: 1.05rem;
    color: var(--red);
    letter-spacing: 0.04em;
    display: flex;
    align-items: center;
    gap: 12px;
    animation: danger-pulse 2s ease-in-out infinite;
}
@keyframes danger-pulse {
    0%, 100% { box-shadow: none; border-color: rgba(248,113,113,0.35); }
    50%       { box-shadow: 0 0 24px rgba(248,113,113,0.12); border-color: rgba(248,113,113,0.6); }
}
.status-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: currentColor;
    flex-shrink: 0;
    box-shadow: 0 0 8px currentColor;
}
.status-text { flex: 1; }
.status-time {
    font-size: 0.8rem;
    font-weight: 500;
    opacity: 0.6;
    margin-left: auto;
}

/* ── PPE Cards ── */
.ppe-card {
    display: flex;
    align-items: center;
    gap: 14px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 18px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.ppe-ok   { border-left: 3px solid var(--green); background: rgba(52,211,153,0.04); }
.ppe-fail {
    border-left: 3px solid var(--red);
    background: rgba(248,113,113,0.05);
    animation: danger-pulse 2s ease-in-out infinite;
}
.ppe-unknown { border-left: 3px solid var(--yellow); background: rgba(251,191,36,0.04); }

.ppe-indicator {
    width: 36px; height: 36px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem; font-weight: 800;
    flex-shrink: 0;
}
.ppe-ind-ok      { background: rgba(52,211,153,0.15); color: var(--green); }
.ppe-ind-fail    { background: rgba(248,113,113,0.15); color: var(--red); }
.ppe-ind-unknown { background: rgba(251,191,36,0.15); color: var(--yellow); }

.ppe-info { flex: 1; min-width: 0; }
.ppe-name { font-weight: 600; font-size: 0.92rem; color: var(--text); margin-bottom: 2px; }
.ppe-state-ok      { font-size: 0.75rem; font-weight: 600; color: var(--green); }
.ppe-state-fail    { font-size: 0.75rem; font-weight: 700; color: var(--red); text-transform: uppercase; }
.ppe-state-unknown { font-size: 0.75rem; font-weight: 600; color: var(--yellow); }

/* ── Sensor Cards ── */
.sensor-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 18px;
    margin-bottom: 10px;
    transition: border-color 0.2s, background 0.2s;
}
.sensor-card:hover {
    border-color: var(--border-h);
    background: var(--card-2);
}
.s-label {
    color: var(--text-muted);
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 6px;
}
.s-value {
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    line-height: 1;
    margin-bottom: 10px;
}
.s-bar-track {
    background: rgba(255,255,255,0.06);
    border-radius: 99px;
    height: 3px;
    overflow: hidden;
    margin-bottom: 4px;
}
.s-bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.6s ease;
}
.s-bar-label {
    font-size: 0.62rem;
    color: var(--text-muted);
    letter-spacing: 0.05em;
}

/* ── Camera wrappers ── */
.cam-wrap-safe    { border: 2px solid rgba(52,211,153,0.4); border-radius: var(--radius-lg); overflow: hidden; }
.cam-wrap-danger  { border: 2px solid rgba(248,113,113,0.5); border-radius: var(--radius-lg); overflow: hidden; animation: danger-pulse 1.5s ease-in-out infinite; }
.cam-wrap-neutral { border: 2px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; }

/* ── Camera badge ── */
.cam-badge-live {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(52,211,153,0.12);
    border: 1px solid rgba(52,211,153,0.3);
    color: var(--green);
    font-size: 0.72rem; font-weight: 700;
    padding: 4px 12px; border-radius: 99px;
    letter-spacing: 0.08em; margin-bottom: 8px;
}
.cam-badge-alert {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(248,113,113,0.12);
    border: 1px solid rgba(248,113,113,0.4);
    color: var(--red);
    font-size: 0.72rem; font-weight: 700;
    padding: 4px 12px; border-radius: 99px;
    letter-spacing: 0.08em; margin-bottom: 8px;
    animation: danger-pulse 1.5s ease-in-out infinite;
}
.cam-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }

/* ── Camera placeholder ── */
.cam-placeholder {
    background: var(--card);
    border: 2px dashed rgba(255,255,255,0.08);
    border-radius: var(--radius-lg);
    padding: 64px 20px;
    text-align: center;
    color: var(--text-muted);
}
.cam-placeholder strong {
    display: block;
    color: var(--text-sub);
    font-size: 0.95rem;
    margin-bottom: 6px;
}

/* ── Violation box ── */
.violation-box {
    background: rgba(248,113,113,0.06);
    border: 1px solid rgba(248,113,113,0.25);
    border-left: 4px solid var(--red);
    border-radius: var(--radius);
    padding: 18px 20px;
    margin-bottom: 16px;
}
.v-title {
    font-size: 0.85rem;
    font-weight: 800;
    color: var(--red);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 6px;
}
.v-sub { font-size: 0.82rem; color: #fca5a5; margin-bottom: 10px; }
.v-item {
    display: flex; align-items: center; gap: 8px;
    padding: 7px 0;
    border-top: 1px solid rgba(248,113,113,0.1);
    font-size: 0.88rem;
    color: #fca5a5;
}
.v-item-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--red); flex-shrink: 0; }

/* ── Violations counter ── */
.viol-count {
    border-radius: var(--radius);
    padding: 10px 18px;
    margin-top: 10px;
    text-align: center;
    font-weight: 700;
    font-size: 0.88rem;
    border: 1px solid;
}
.viol-safe   { background: rgba(52,211,153,0.07); border-color: rgba(52,211,153,0.2); color: var(--green); }
.viol-danger { background: rgba(248,113,113,0.07); border-color: rgba(248,113,113,0.25); color: var(--red); }

/* ── Alert reasons ── */
.alert-reason {
    background: rgba(251,191,36,0.07);
    border: 1px solid rgba(251,191,36,0.2);
    border-radius: 8px;
    padding: 8px 14px;
    margin-bottom: 6px;
    color: var(--yellow);
    font-size: 0.85rem;
    font-weight: 500;
}

/* ── Info card ── */
.info-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 18px;
    margin-bottom: 10px;
}
.info-card .label {
    color: var(--text-muted);
    font-size: 0.65rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.12em;
    margin-bottom: 4px;
}
.info-card .value {
    font-size: 1.5rem; font-weight: 800;
    color: var(--text); letter-spacing: -0.4px;
}

/* ── Factory header ── */
.factory-header {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 12px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-bottom: 18px;
    flex-wrap: wrap;
}
.fh-item { font-size: 0.8rem; color: var(--text-sub); }
.fh-item strong { color: var(--text); font-weight: 700; }

/* ── Connection badge ── */
.conn-online  { display: inline-flex; align-items: center; gap: 6px; color: var(--green); font-size: 0.8rem; font-weight: 600; }
.conn-offline { display: inline-flex; align-items: center; gap: 6px; color: var(--red); font-size: 0.8rem; font-weight: 600; }
.conn-dot     { width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
.conn-dot-on  { box-shadow: 0 0 6px currentColor; }

/* ── Section dividers ── */
.section-head {
    display: flex; align-items: center; gap: 12px;
    margin: 30px 0 18px;
}
.section-head-text {
    font-size: 0.68rem; font-weight: 700;
    color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.14em;
    white-space: nowrap;
}
.section-head-line {
    flex: 1; height: 1px;
    background: linear-gradient(90deg, var(--border), transparent);
}

/* ── Buttons ── */
button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.2s, transform 0.1s !important;
    box-shadow: 0 2px 12px rgba(37,99,235,0.35) !important;
}
button[kind="primary"]:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
button[kind="secondary"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-sub) !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    transition: border-color 0.2s, background 0.2s !important;
}
button[kind="secondary"]:hover {
    border-color: var(--border-h) !important;
    background: var(--card-2) !important;
}

/* ── HR ── */
hr { border-color: var(--border) !important; margin: 28px 0 !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
    color: var(--text-muted) !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--blue) !important;
}
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid var(--border) !important;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 9px !important;
    color: var(--text) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(77,142,247,0.12) !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 9px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 99px; }

/* ── Mobile responsive ── */
@media (max-width: 768px) {
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    .block-container {
        padding: 1rem 0.75rem 1.5rem !important;
        max-width: 100% !important;
    }
    h1 { font-size: 1.3rem !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 1.45rem !important; }
    .s-value { font-size: 1.25rem !important; }
    .status-safe, .status-warning, .status-danger { font-size: 0.9rem !important; padding: 12px 16px !important; }
    .factory-header { flex-direction: column !important; align-items: flex-start !important; }
    [data-testid="stSidebar"] { width: 100vw !important; max-width: 100vw !important; }
    [data-testid="stDataFrame"] { overflow-x: auto !important; }
    button[kind="primary"], button[kind="secondary"] { width: 100% !important; }
}
@media (max-width: 480px) {
    h1 { font-size: 1.1rem !important; }
    .block-container { padding: 0.75rem 0.5rem 1rem !important; }
    .status-safe, .status-warning, .status-danger { font-size: 0.82rem !important; padding: 10px 12px !important; }
}
</style>
"""

COLORS = {
    "safe":       "#34d399",
    "warning":    "#fbbf24",
    "danger":     "#f87171",
    "blue":       "#4d8ef7",
    "purple":     "#a78bfa",
    "cyan":       "#22d3ee",
    "orange":     "#fb923c",
    "grid":       "#1a2540",
    "background": "#080c14",
    "paper":      "#101828",
    "text":       "#e8edf5",
    "subtext":    "#8fa3c0",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor=COLORS["paper"],
    plot_bgcolor =COLORS["background"],
    font         =dict(color=COLORS["text"], size=12, family="Inter, Segoe UI, sans-serif"),
    xaxis        =dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"], showgrid=True),
    yaxis        =dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"], showgrid=True),
    margin       =dict(l=50, r=20, t=40, b=40),
    legend       =dict(bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS["subtext"])),
)
