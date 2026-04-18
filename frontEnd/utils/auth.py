"""
Authentication helpers — credentials, session state, and page guards.
"""
import streamlit as st

# ── Credentials store ─────────────────────────────────────────────
# key: username (case-insensitive)  value: {password, role, display_name}
USERS: dict = {
    "admin": {
        "password":     "admin123",
        "role":         "Admin",
        "display_name": "Administrator",
    },
    "manager": {
        "password":     "manager123",
        "role":         "Admin",
        "display_name": "Site Manager",
    },
    "staff": {
        "password":     "staff123",
        "role":         "Staff",
        "display_name": "Staff Member",
    },
    "worker": {
        "password":     "worker123",
        "role":         "Staff",
        "display_name": "Site Worker",
    },
}

ROLE_ADMIN = "Admin"
ROLE_STAFF = "Staff"


# ── Session helpers ───────────────────────────────────────────────

def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def current_role() -> str:
    return st.session_state.get("role", "")


def current_user() -> str:
    return st.session_state.get("display_name", "")


def login(username: str, password: str) -> tuple[bool, str]:
    """
    Attempt login. Returns (success, error_message).
    Sets session state on success.
    """
    user = USERS.get(username.lower().strip())
    if user is None:
        return False, "Username not found."
    if user["password"] != password:
        return False, "Incorrect password."

    st.session_state["logged_in"]    = True
    st.session_state["username"]     = username.lower().strip()
    st.session_state["role"]         = user["role"]
    st.session_state["display_name"] = user["display_name"]
    return True, ""


def logout():
    for key in ["logged_in", "username", "role", "display_name"]:
        st.session_state.pop(key, None)


# ── Page guards ───────────────────────────────────────────────────

def require_login():
    """
    Call at the top of every page.
    Stops the page and shows a redirect notice if the user is not logged in.
    """
    if not is_logged_in():
        st.markdown("""
        <style>
        html,body,[data-testid="stAppViewContainer"]{background:#0d1117;color:#e6edf3;}
        [data-testid="stSidebar"]{display:none;}
        </style>
        """, unsafe_allow_html=True)
        st.warning("You must be logged in to view this page.")
        if st.button("Go to Login", type="primary"):
            st.switch_page("app.py")
        st.stop()


def require_admin():
    """
    Call on admin-only pages after require_login().
    Blocks Staff users from accessing the page.
    """
    require_login()
    if current_role() != ROLE_ADMIN:
        st.error("Access denied. This page is for Admin / Manager only.")
        if st.button("Go to Staff View"):
            st.switch_page("pages/1_Staff_View.py")
        st.stop()


def sidebar_user_info():
    """Render the logged-in user chip and logout button in the sidebar."""
    role_color = "#58a6ff" if current_role() == ROLE_ADMIN else "#3fb950"
    st.sidebar.markdown(
        f'<div style="background:#161b22;border:1px solid #30363d;border-radius:10px;'
        f'padding:10px 14px;margin-bottom:12px;">'
        f'<div style="color:#8b949e;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.06em;">Logged in as</div>'
        f'<div style="color:#e6edf3;font-weight:700;font-size:1rem;margin-top:2px;">{current_user()}</div>'
        f'<div style="color:{role_color};font-size:0.8rem;margin-top:2px;">● {current_role()}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")
