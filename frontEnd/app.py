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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

[data-testid="stSidebar"],
[data-testid="stSidebarNavItems"],
#MainMenu, footer, header { display: none !important; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080c14;
    color: #e8edf5;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}

/* Subtle grid background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(77,142,247,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(77,142,247,0.03) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

.block-container {
    position: relative;
    z-index: 1;
    padding-top: 4rem !important;
    max-width: 480px !important;
}

/* ── Login card ── */
.login-header {
    text-align: center;
    margin-bottom: 36px;
}
.login-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(77,142,247,0.1);
    border: 1px solid rgba(77,142,247,0.25);
    border-radius: 99px;
    padding: 5px 16px;
    font-size: 0.72rem;
    font-weight: 700;
    color: #4d8ef7;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 18px;
}
.login-badge-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #4d8ef7;
    box-shadow: 0 0 6px #4d8ef7;
}
.login-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: #e8edf5;
    letter-spacing: -0.5px;
    line-height: 1.2;
    margin-bottom: 8px;
}
.login-sub {
    font-size: 0.85rem;
    color: #8fa3c0;
    line-height: 1.5;
}

/* ── Form section ── */
.form-section {
    background: #0f1828;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 32px 36px 28px;
    box-shadow: 0 24px 64px rgba(0,0,0,0.5);
    margin-bottom: 16px;
}
.form-label {
    color: #4a6080;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 6px;
}
.divider-line {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 22px 0;
}

/* ── Streamlit overrides ── */
[data-testid="stTextInput"] input {
    background: #0a1020 !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    color: #e8edf5 !important;
    font-size: 0.92rem !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #4d8ef7 !important;
    box-shadow: 0 0 0 3px rgba(77,142,247,0.12) !important;
}
[data-testid="stTextInput"] label {
    color: #4a6080 !important;
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 12px !important;
    width: 100% !important;
    box-shadow: 0 4px 16px rgba(37,99,235,0.35) !important;
    transition: opacity 0.2s, transform 0.1s !important;
    letter-spacing: 0.02em !important;
}
button[kind="primary"]:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── Credentials hint ── */
.creds-card {
    background: #0a1020;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 18px 20px;
}
.creds-title {
    font-size: 0.68rem;
    font-weight: 700;
    color: #4a6080;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 14px;
}
.creds-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
    font-size: 0.82rem;
}
.creds-row:last-child { margin-bottom: 0; }
.role-tag {
    display: inline-block;
    border-radius: 6px;
    padding: 2px 9px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    flex-shrink: 0;
}
.role-admin { background: rgba(77,142,247,0.12); color: #4d8ef7; border: 1px solid rgba(77,142,247,0.25); }
.role-staff { background: rgba(52,211,153,0.1); color: #34d399; border: 1px solid rgba(52,211,153,0.2); }
.creds-text { color: #8fa3c0; }
.creds-text strong { color: #c8d5e8; font-weight: 600; }

@media (max-width: 480px) {
    .block-container { padding-top: 2rem !important; max-width: 100% !important; }
    .form-section { padding: 24px 20px 20px !important; border-radius: 14px !important; }
    .login-title { font-size: 1.4rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="login-header">
    <div><span class="login-badge"><span class="login-badge-dot"></span>Edge AI System</span></div>
    <div class="login-title">Construction Safety<br>Monitor</div>
    <div class="login-sub">Real-time PPE detection &amp; environmental monitoring<br>powered by Edge AI</div>
</div>
""", unsafe_allow_html=True)

# ── Form ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="form-section">', unsafe_allow_html=True)

with st.form("login_form", clear_on_submit=False):
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", placeholder="Enter your password", type="password")
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

    if submitted:
        if not username.strip():
            st.error("Please enter your username.")
        elif not password:
            st.error("Please enter your password.")
        else:
            success, error_msg = login(username, password)
            if success:
                st.success("Login successful! Redirecting…")
                st.rerun()
            else:
                st.error(f"Login failed: {error_msg}")

st.markdown("</div>", unsafe_allow_html=True)

