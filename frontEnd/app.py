"""
Edge AI – Construction Safety Monitor
Login page — entry point for all users.
Run with:
    cd frontEnd
    streamlit run app.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from utils.auth import is_logged_in, login, current_role, ROLE_ADMIN

st.set_page_config(
    page_title="Safety Monitor — Login",
    page_icon="🦺",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Redirect if already logged in ────────────────────────────────────────────
if is_logged_in():
    if current_role() == ROLE_ADMIN:
        st.switch_page("pages/2_Admin_View.py")
    else:
        st.switch_page("pages/1_Staff_View.py")

# ── Page styles ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Hide sidebar and default chrome */
[data-testid="stSidebar"],
[data-testid="stSidebarNavItems"],
#MainMenu, footer, header { display: none !important; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: 'Segoe UI', system-ui, sans-serif;
}

/* Login card */
.login-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 40px 48px 36px;
    max-width: 440px;
    margin: 0 auto;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.login-logo {
    text-align: center;
    margin-bottom: 8px;
}
.login-title {
    text-align: center;
    font-size: 1.6rem;
    font-weight: 700;
    color: #58a6ff;
    letter-spacing: -0.3px;
    margin-bottom: 4px;
}
.login-sub {
    text-align: center;
    font-size: 0.85rem;
    color: #8b949e;
    margin-bottom: 28px;
}
.divider {
    border: none;
    border-top: 1px solid #30363d;
    margin: 20px 0;
}
.role-badge-admin {
    display: inline-block;
    background: #132033;
    border: 1px solid #1f6feb;
    color: #58a6ff;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 600;
}
.role-badge-staff {
    display: inline-block;
    background: #0d2818;
    border: 1px solid #238636;
    color: #3fb950;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 600;
}
.creds-table {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 0.82rem;
    color: #8b949e;
    margin-top: 20px;
}
.creds-table strong { color: #c9d1d9; }

/* Streamlit input overrides */
[data-testid="stTextInput"] input {
    background: #0d1117 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
    font-size: 0.95rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 3px rgba(88,166,255,0.15) !important;
}
[data-testid="stTextInput"] label {
    color: #8b949e !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
button[kind="primary"] {
    background: #1f6feb !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 10px !important;
    width: 100% !important;
    transition: background 0.2s;
}
button[kind="primary"]:hover {
    background: #388bfd !important;
}
</style>
""", unsafe_allow_html=True)

# ── Login card ────────────────────────────────────────────────────────────────
st.markdown('<div class="login-logo"><img src="https://img.icons8.com/color/96/hard-hat.png" width="72"/></div>', unsafe_allow_html=True)
st.markdown('<div class="login-title">Construction Safety Monitor</div>', unsafe_allow_html=True)
st.markdown('<div class="login-sub">Edge AI — Real-time PPE & Environmental Monitoring</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── Login form ────────────────────────────────────────────────────────────────
with st.form("login_form", clear_on_submit=False):
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", placeholder="Enter your password", type="password")
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

# ── Default credentials hint ──────────────────────────────────────────────────
st.markdown("""
<div class="creds-table">
    <div style="margin-bottom:10px;color:#c9d1d9;font-weight:600;">Demo Credentials</div>
    <div style="margin-bottom:6px;">
        <span class="role-badge-admin">Admin</span>
        &nbsp; <strong>admin</strong> / admin123 &nbsp;·&nbsp; <strong>manager</strong> / manager123
    </div>
    <div>
        <span class="role-badge-staff">Staff</span>
        &nbsp; <strong>staff</strong> / staff123 &nbsp;·&nbsp; <strong>worker</strong> / worker123
    </div>
</div>
""", unsafe_allow_html=True)
