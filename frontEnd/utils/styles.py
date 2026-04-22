"""
Design system — Industrial Brutalist Safety Theme.
Font: Rajdhani (display) + DM Mono (data) — sharp, utilitarian, memorable.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=DM+Mono:wght@400;500&family=Inter:wght@400;500;600;700&display=swap');

/* ── Design tokens ── */
:root {
  --bg:        #0a0a0a;
  --surface:   #111111;
  --card:      #161616;
  --card-2:    #1c1c1c;
  --border:    rgba(255,255,255,0.06);
  --border-h:  rgba(255,255,255,0.13);

  --amber:     #f59e0b;
  --amber-dim: rgba(245,158,11,0.12);
  --amber-glow:rgba(245,158,11,0.25);
  --green:     #22c55e;
  --green-bg:  rgba(34,197,94,0.08);
  --yellow:    #eab308;
  --yellow-bg: rgba(234,179,8,0.08);
  --red:       #ef4444;
  --red-bg:    rgba(239,68,68,0.08);
  --blue:      #3b82f6;
  --cyan:      #06b6d4;
  --purple:    #8b5cf6;
  --orange:    #f97316;

  --text:      #f0f0f0;
  --text-sub:  #a0a0a0;
  --text-muted:#555555;

  --font-display: 'Rajdhani', 'Inter', system-ui, sans-serif;
  --font-mono:    'DM Mono', 'Courier New', monospace;
  --font-body:    'Inter', system-ui, sans-serif;

  --radius:    6px;
  --radius-lg: 8px;
  --radius-xl: 10px;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}

/* Scan-line texture overlay */
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.08) 2px,
        rgba(0,0,0,0.08) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

/* Corner bracket accent on main content */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--amber) 0%, transparent 60%);
    z-index: 100;
}

.block-container {
    padding-top: 1.6rem !important;
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
    font-family: var(--font-display) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    line-height: 1.1 !important;
}
h2 {
    color: var(--amber) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.2em !important;
}
h3 {
    color: var(--text) !important;
    font-family: var(--font-display) !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}
h4 {
    color: var(--text-sub) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.18em !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-top: 2px solid var(--amber) !important;
    border-radius: var(--radius) !important;
    padding: 18px 20px !important;
    transition: border-color 0.2s, background 0.2s;
    position: relative;
    overflow: hidden;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, var(--amber-glow), transparent);
}
[data-testid="metric-container"]:hover {
    border-color: rgba(245,158,11,0.4) !important;
    background: var(--card-2) !important;
}
[data-testid="metric-container"] label {
    color: var(--text-muted) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.62rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.15em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: var(--font-display) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    letter-spacing: 0.02em !important;
}

/* ── Status banners ── */
.status-safe {
    background: var(--green-bg);
    border: 1px solid rgba(34,197,94,0.2);
    border-left: 3px solid var(--green);
    border-radius: var(--radius);
    padding: 14px 20px;
    margin-bottom: 18px;
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 1rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--green);
    display: flex;
    align-items: center;
    gap: 12px;
}
.status-warning {
    background: var(--yellow-bg);
    border: 1px solid rgba(234,179,8,0.2);
    border-left: 3px solid var(--yellow);
    border-radius: var(--radius);
    padding: 14px 20px;
    margin-bottom: 18px;
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 1rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--yellow);
    display: flex;
    align-items: center;
    gap: 12px;
}
.status-danger {
    background: var(--red-bg);
    border: 1px solid rgba(239,68,68,0.2);
    border-left: 3px solid var(--red);
    border-radius: var(--radius);
    padding: 14px 20px;
    margin-bottom: 18px;
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 1rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--red);
    display: flex;
    align-items: center;
    gap: 12px;
    animation: danger-pulse 2s ease-in-out infinite;
}
@keyframes danger-pulse {
    0%, 100% { box-shadow: none; border-left-color: rgba(239,68,68,0.5); }
    50%       { box-shadow: inset 0 0 40px rgba(239,68,68,0.04), 0 0 20px rgba(239,68,68,0.08); border-left-color: var(--red); }
}
.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: currentColor;
    flex-shrink: 0;
    box-shadow: 0 0 8px currentColor;
    animation: dot-blink 1.4s ease-in-out infinite;
}
@keyframes dot-blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}
.status-text { flex: 1; }
.status-time {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    font-weight: 400;
    opacity: 0.5;
    margin-left: auto;
    letter-spacing: 0.05em;
}

/* ── PPE Cards ── */
.ppe-card {
    display: flex;
    align-items: center;
    gap: 14px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 16px;
    margin-bottom: 8px;
    transition: border-color 0.2s;
}
.ppe-ok      { border-left: 3px solid var(--green); }
.ppe-fail    {
    border-left: 3px solid var(--red);
    background: rgba(239,68,68,0.04);
    animation: danger-pulse 2s ease-in-out infinite;
}
.ppe-unknown { border-left: 3px solid var(--text-muted); }

.ppe-indicator {
    width: 34px; height: 34px;
    border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    font-family: var(--font-display);
    font-size: 0.8rem; font-weight: 700;
    letter-spacing: 0.05em;
    flex-shrink: 0;
}
.ppe-ind-ok      { background: rgba(34,197,94,0.12); color: var(--green); }
.ppe-ind-fail    { background: rgba(239,68,68,0.12); color: var(--red); }
.ppe-ind-unknown { background: rgba(255,255,255,0.05); color: var(--text-muted); }

.ppe-info { flex: 1; min-width: 0; }
.ppe-name {
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.04em;
    color: var(--text);
    margin-bottom: 2px;
    text-transform: uppercase;
}
.ppe-state-ok      { font-family: var(--font-mono); font-size: 0.68rem; color: var(--green); letter-spacing: 0.08em; }
.ppe-state-fail    { font-family: var(--font-mono); font-size: 0.68rem; font-weight: 500; color: var(--red); text-transform: uppercase; letter-spacing: 0.08em; }
.ppe-state-unknown { font-family: var(--font-mono); font-size: 0.68rem; color: var(--text-muted); letter-spacing: 0.08em; }

/* ── Sensor Cards ── */
.sensor-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 16px;
    margin-bottom: 8px;
    transition: border-color 0.2s, background 0.2s;
    position: relative;
    overflow: hidden;
}
.sensor-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
}
.sensor-card:hover {
    border-color: var(--border-h);
    background: var(--card-2);
}
.s-label {
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 0.6rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 6px;
}
.s-value {
    font-family: var(--font-display);
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    line-height: 1;
    margin-bottom: 10px;
}
.s-bar-track {
    background: rgba(255,255,255,0.04);
    border-radius: 0;
    height: 2px;
    overflow: hidden;
    margin-bottom: 4px;
}
.s-bar-fill {
    height: 100%;
    border-radius: 0;
    transition: width 0.6s ease;
}
.s-bar-label {
    font-family: var(--font-mono);
    font-size: 0.58rem;
    color: var(--text-muted);
    letter-spacing: 0.08em;
}

/* ── Camera wrappers ── */
.cam-wrap-safe    { border: 1px solid rgba(34,197,94,0.3); border-radius: var(--radius-lg); overflow: hidden; }
.cam-wrap-danger  { border: 1px solid rgba(239,68,68,0.4); border-radius: var(--radius-lg); overflow: hidden; animation: danger-pulse 1.5s ease-in-out infinite; }
.cam-wrap-neutral { border: 1px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; }

/* ── Camera badges ── */
.cam-badge-live {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.25);
    color: var(--green);
    font-family: var(--font-mono);
    font-size: 0.65rem; font-weight: 500;
    padding: 3px 10px; border-radius: 2px;
    letter-spacing: 0.12em; margin-bottom: 8px;
    text-transform: uppercase;
}
.cam-badge-alert {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.3);
    color: var(--red);
    font-family: var(--font-mono);
    font-size: 0.65rem; font-weight: 500;
    padding: 3px 10px; border-radius: 2px;
    letter-spacing: 0.12em; margin-bottom: 8px;
    text-transform: uppercase;
    animation: danger-pulse 1.5s ease-in-out infinite;
}
.cam-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; animation: dot-blink 1.4s ease-in-out infinite; }

/* ── Camera placeholder ── */
.cam-placeholder {
    background: var(--card);
    border: 1px dashed rgba(255,255,255,0.06);
    border-radius: var(--radius-lg);
    padding: 64px 20px;
    text-align: center;
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 0.78rem;
    letter-spacing: 0.06em;
}
.cam-placeholder strong {
    display: block;
    color: var(--text-sub);
    font-family: var(--font-display);
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 6px;
}

/* ── Violation box ── */
.violation-box {
    background: rgba(239,68,68,0.05);
    border: 1px solid rgba(239,68,68,0.2);
    border-left: 3px solid var(--red);
    border-radius: var(--radius);
    padding: 16px 18px;
    margin-bottom: 14px;
}
.v-title {
    font-family: var(--font-display);
    font-size: 0.88rem;
    font-weight: 700;
    color: var(--red);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 4px;
}
.v-sub {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: rgba(239,68,68,0.6);
    margin-bottom: 10px;
    letter-spacing: 0.04em;
}
.v-item {
    display: flex; align-items: center; gap: 8px;
    padding: 7px 0;
    border-top: 1px solid rgba(239,68,68,0.08);
    font-family: var(--font-mono);
    font-size: 0.8rem;
    color: rgba(239,68,68,0.8);
    letter-spacing: 0.04em;
}
.v-item-dot { width: 4px; height: 4px; border-radius: 50%; background: var(--red); flex-shrink: 0; }

/* ── Violations counter ── */
.viol-count {
    border-radius: var(--radius);
    padding: 8px 16px;
    margin-top: 8px;
    text-align: center;
    font-family: var(--font-mono);
    font-weight: 500;
    font-size: 0.78rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border: 1px solid;
}
.viol-safe   { background: rgba(34,197,94,0.05); border-color: rgba(34,197,94,0.15); color: var(--green); }
.viol-danger { background: rgba(239,68,68,0.05); border-color: rgba(239,68,68,0.2); color: var(--red); }

/* ── Alert reasons ── */
.alert-reason {
    background: rgba(234,179,8,0.05);
    border: 1px solid rgba(234,179,8,0.15);
    border-left: 2px solid var(--yellow);
    border-radius: var(--radius);
    padding: 7px 12px;
    margin-bottom: 5px;
    color: var(--yellow);
    font-family: var(--font-mono);
    font-size: 0.75rem;
    letter-spacing: 0.06em;
}

/* ── Info card ── */
.info-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 16px;
    margin-bottom: 8px;
}
.info-card .label {
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 0.6rem; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.14em;
    margin-bottom: 4px;
}
.info-card .value {
    font-family: var(--font-display);
    font-size: 1.5rem; font-weight: 700;
    color: var(--text); letter-spacing: 0.02em;
    text-transform: uppercase;
}

/* ── Factory header ── */
.factory-header {
    background: var(--card);
    border: 1px solid var(--border);
    border-top: 2px solid rgba(245,158,11,0.4);
    border-radius: var(--radius);
    padding: 10px 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    flex-wrap: wrap;
}
.fh-item {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--text-muted);
    letter-spacing: 0.06em;
}
.fh-item strong { color: var(--text); font-weight: 500; }

/* ── Connection badge ── */
.conn-online  { display: inline-flex; align-items: center; gap: 6px; color: var(--green); font-family: var(--font-mono); font-size: 0.72rem; letter-spacing: 0.06em; }
.conn-offline { display: inline-flex; align-items: center; gap: 6px; color: var(--red); font-family: var(--font-mono); font-size: 0.72rem; letter-spacing: 0.06em; }
.conn-dot     { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.conn-dot-on  { box-shadow: 0 0 6px currentColor; animation: dot-blink 1.4s ease-in-out infinite; }

/* ── Section dividers ── */
.section-head {
    display: flex; align-items: center; gap: 12px;
    margin: 28px 0 16px;
}
.section-head-text {
    font-family: var(--font-mono);
    font-size: 0.6rem; font-weight: 500;
    color: var(--amber); text-transform: uppercase; letter-spacing: 0.18em;
    white-space: nowrap;
}
.section-head-line {
    flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(245,158,11,0.3), transparent);
}

/* ── Buttons ── */
button[kind="primary"] {
    background: var(--amber) !important;
    color: #000 !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-family: var(--font-display) !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    transition: opacity 0.2s, transform 0.1s !important;
    box-shadow: none !important;
}
button[kind="primary"]:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
button[kind="secondary"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-sub) !important;
    border-radius: var(--radius) !important;
    font-family: var(--font-display) !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    transition: border-color 0.2s, background 0.2s !important;
}
button[kind="secondary"]:hover {
    border-color: var(--border-h) !important;
    background: var(--card-2) !important;
}

/* ── HR ── */
hr { border-color: var(--border) !important; margin: 24px 0 !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
    color: var(--text-muted) !important;
    font-family: var(--font-display) !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--amber) !important;
}
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid var(--border) !important;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.85rem !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 2px var(--amber-dim) !important;
}
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label {
    color: var(--text-muted) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.62rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* ── Sliders ── */
[data-testid="stSlider"] [role="slider"] {
    background: var(--amber) !important;
    border-color: var(--amber) !important;
}
[data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSlider"] [data-testid="stTickBarMax"] {
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    color: var(--text-muted) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(245,158,11,0.2); border-radius: 0; }
::-webkit-scrollbar-thumb:hover { background: rgba(245,158,11,0.4); }

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
    h1 { font-size: 1.5rem !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 1.6rem !important; }
    .s-value { font-size: 1.3rem !important; }
    .status-safe, .status-warning, .status-danger { font-size: 0.88rem !important; padding: 10px 14px !important; }
    .factory-header { flex-direction: column !important; align-items: flex-start !important; }
    [data-testid="stSidebar"] { width: 100vw !important; max-width: 100vw !important; }
    [data-testid="stDataFrame"] { overflow-x: auto !important; }
    button[kind="primary"], button[kind="secondary"] { width: 100% !important; }
}
@media (max-width: 480px) {
    h1 { font-size: 1.2rem !important; }
    .block-container { padding: 0.75rem 0.5rem 1rem !important; }
}
</style>
"""

COLORS = {
    "safe":       "#22c55e",
    "warning":    "#eab308",
    "danger":     "#ef4444",
    "blue":       "#3b82f6",
    "purple":     "#8b5cf6",
    "cyan":       "#06b6d4",
    "orange":     "#f97316",
    "amber":      "#f59e0b",
    "grid":       "#1a1a1a",
    "background": "#0a0a0a",
    "paper":      "#161616",
    "text":       "#f0f0f0",
    "subtext":    "#a0a0a0",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor=COLORS["paper"],
    plot_bgcolor =COLORS["background"],
    font         =dict(color=COLORS["text"], size=11, family="DM Mono, Courier New, monospace"),
    xaxis        =dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"], showgrid=True),
    yaxis        =dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"], showgrid=True),
    margin       =dict(l=50, r=20, t=40, b=40),
    legend       =dict(bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS["subtext"])),
)