"""
Edge AI — Construction Safety Monitor
Login page — entry point for all users.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from utils.auth import is_logged_in, login, current_role, ROLE_ADMIN

st.set_page_config(
    page_title="Safety Monitor — Login",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if is_logged_in():
    if current_role() == ROLE_ADMIN:
        st.switch_page("pages/2_Admin_View.py")
    else:
        st.switch_page("pages/1_Staff_View.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

[data-testid="stSidebar"],
[data-testid="stSidebarNavItems"],
#MainMenu, footer, header { display: none !important; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0a;
    color: #f0f0f0;
    font-family: 'Inter', system-ui, sans-serif;
}

/* Top amber line */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #f59e0b 0%, transparent 60%);
    z-index: 100;
}

/* Scan-line texture */
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image: repeating-linear-gradient(
        0deg, transparent, transparent 2px,
        rgba(0,0,0,0.07) 2px, rgba(0,0,0,0.07) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

/* Subtle grid */
[data-testid="stMain"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(245,158,11,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(245,158,11,0.025) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

.block-container {
    position: relative;
    z-index: 1;
    padding-top: 5rem !important;
    max-width: 440px !important;
}

/* Header */
.login-header { text-align: center; margin-bottom: 32px; }
.login-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(245,158,11,0.08);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: 2px;
    padding: 4px 14px;
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    font-weight: 500;
    color: #f59e0b;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 16px;
}
.login-badge-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: #f59e0b;
    box-shadow: 0 0 6px #f59e0b;
    animation: blink 1.4s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.2;} }

.login-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #f0f0f0;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    line-height: 1.1;
    margin-bottom: 8px;
}
.login-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #555;
    line-height: 1.6;
    letter-spacing: 0.04em;
}

/* Form card */
.form-section {
    background: #111111;
    border: 1px solid rgba(255,255,255,0.06);
    border-top: 2px solid #f59e0b;
    border-radius: 6px;
    padding: 28px 32px 24px;
    box-shadow: 0 32px 80px rgba(0,0,0,0.6);
    margin-bottom: 14px;
    position: relative;
}

/* Streamlit input overrides */
[data-testid="stTextInput"] input {
    background: #0a0a0a !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 4px !important;
    color: #f0f0f0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
    padding: 10px 12px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #f59e0b !important;
    box-shadow: 0 0 0 2px rgba(245,158,11,0.1) !important;
}
[data-testid="stTextInput"] label {
    color: #555 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.6rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.14em !important;
}
button[kind="primary"] {
    background: #f59e0b !important;
    color: #000 !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 12px !important;
    width: 100% !important;
    transition: opacity 0.2s, transform 0.1s !important;
}
button[kind="primary"]:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }

/* Credentials hint */
.creds-card {
    background: #0d0d0d;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 4px;
    padding: 14px 16px;
}
.creds-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    font-weight: 500;
    color: #444;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    margin-bottom: 12px;
}
.creds-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 7px;
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
}
.creds-row:last-child { margin-bottom: 0; }
.role-tag {
    display: inline-block;
    border-radius: 2px;
    padding: 1px 8px;
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    flex-shrink: 0;
}
.role-admin { background: rgba(245,158,11,0.1); color: #f59e0b; border: 1px solid rgba(245,158,11,0.2); }
.role-staff { background: rgba(34,197,94,0.08); color: #22c55e; border: 1px solid rgba(34,197,94,0.15); }
.creds-text { color: #555; }
.creds-text strong { color: #888; font-weight: 500; }

@media (max-width: 480px) {
    .block-container { padding-top: 2rem !important; max-width: 100% !important; }
    .form-section { padding: 20px 16px 18px !important; }
    .login-title { font-size: 1.7rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="login-header">
    <div><span class="login-badge"><span class="login-badge-dot"></span>Edge AI System</span></div>
    <div class="login-title">Construction<br>Safety Monitor</div>
    <div class="login-sub">Real-time PPE detection &amp; environmental monitoring<br>powered by edge inference</div>
</div>
""", unsafe_allow_html=True)

# ── Form ───────────────────────────────────────────────────────────────────
st.markdown('<div class="form-section">', unsafe_allow_html=True)

with st.form("login_form", clear_on_submit=False):
    username = st.text_input("Username", placeholder="enter username")
    password = st.text_input("Password", placeholder="enter password", type="password")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Authenticate", type="primary", use_container_width=True)

    if submitted:
        if not username.strip():
            st.error("Username required.")
        elif not password:
            st.error("Password required.")
        else:
            success, error_msg = login(username, password)
            if success:
                st.success("Access granted. Redirecting…")
                st.rerun()
            else:
                st.error(f"Access denied — {error_msg}")

st.markdown("</div>", unsafe_allow_html=True)

# ── Credentials hint ───────────────────────────────────────────────────────
st.markdown("""
<div class="creds-card">
    <div class="creds-title">// Demo credentials</div>
    <div class="creds-row">
        <span class="role-tag role-admin">Admin</span>
        <span class="creds-text"><strong>admin</strong> / admin123</span>
    </div>
    <div class="creds-row">
        <span class="role-tag role-admin">Admin</span>
        <span class="creds-text"><strong>manager</strong> / manager123</span>
    </div>
    <div class="creds-row">
        <span class="role-tag role-staff">Staff</span>
        <span class="creds-text"><strong>staff</strong> / staff123</span>
    </div>
    <div class="creds-row">
        <span class="role-tag role-staff">Staff</span>
        <span class="creds-text"><strong>worker</strong> / worker123</span>
    </div>
</div>
""", unsafe_allow_html=True)