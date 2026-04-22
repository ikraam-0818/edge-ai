"""
Authentication helpers — credentials, session state, and page guards.
"""
import streamlit as st

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


def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def current_role() -> str:
    return st.session_state.get("role", "")


def current_user() -> str:
    return st.session_state.get("display_name", "")


def login(username: str, password: str) -> tuple[bool, str]:
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


def require_login():
    if not is_logged_in():
        st.markdown("""
        <style>
        html,body,[data-testid="stAppViewContainer"]{background:#080c14;color:#e8edf5;}
        [data-testid="stSidebar"]{display:none;}
        </style>
        """, unsafe_allow_html=True)
        st.warning("You must be logged in to view this page.")
        if st.button("Go to Login", type="primary"):
            st.switch_page("app.py")
        st.stop()


def require_admin():
    require_login()
    if current_role() != ROLE_ADMIN:
        st.error("Access denied. This page is for Admin / Manager only.")
        if st.button("Go to Staff View"):
            st.switch_page("pages/1_Staff_View.py")
        st.stop()


def sidebar_user_info():
    """Render the user card and logout button in the sidebar."""
    name = current_user()
    role = current_role()
    initials = "".join(p[0].upper() for p in name.split() if p)[:2]
    role_color = "#4d8ef7" if role == ROLE_ADMIN else "#34d399"
    role_bg    = "rgba(77,142,247,0.12)" if role == ROLE_ADMIN else "rgba(52,211,153,0.12)"

    st.sidebar.markdown(
        f'<div style="background:#101828;border:1px solid rgba(255,255,255,0.07);'
        f'border-radius:12px;padding:14px 16px;margin-bottom:14px;">'
        f'<div style="display:flex;align-items:center;gap:12px;">'
        f'<div style="width:38px;height:38px;border-radius:10px;background:{role_bg};'
        f'display:flex;align-items:center;justify-content:center;'
        f'font-size:0.9rem;font-weight:800;color:{role_color};flex-shrink:0;">{initials}</div>'
        f'<div style="min-width:0;">'
        f'<div style="font-weight:700;font-size:0.88rem;color:#e8edf5;'
        f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{name}</div>'
        f'<div style="font-size:0.72rem;font-weight:600;color:{role_color};margin-top:2px;">{role}</div>'
        f'</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")
