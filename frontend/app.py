"""
EventSnap AI — Main application entry point.
Linear-inspired dark SaaS shell with workspace navigation.
"""
import streamlit as st
from utils.api_client import api_client
from utils.theme import inject_theme, get_logo_image, get_logo_html

logo_img = get_logo_image()

# ── Page Config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EventLens",
    page_icon=logo_img if logo_img else "📸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject Theme ─────────────────────────────────────────────────────────
inject_theme()

# ── Session State Defaults ───────────────────────────────────────────────
_defaults = {
    "authenticated": False,
    "email": "",
    "user_role": "",
    "user_id": None,
    "current_page": "landing",
    "current_event_id": None,
    "workspace_tab": "Overview",
}
for key, val in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Check for Guest QR Code Flow ─────────────────────────────────────────
query_params = st.query_params
event_id_param = query_params.get("event_id")


# ── Header Navigation for Unauthenticated ────────────────────────────────
if not st.session_state.authenticated:

    if event_id_param:
        # Guest QR flow — show header + guest portal
        c_logo, _ = st.columns([3, 7])
        with c_logo:
            st.markdown(get_logo_html(), unsafe_allow_html=True)
        st.markdown("<hr style='margin: 8px 0 24px 0; opacity: 0.3;'>", unsafe_allow_html=True)

        from components.guest import show_guest_portal
        show_guest_portal(event_id_param)

    elif st.session_state.current_page == "login":
        # Auth form page
        c_logo, _, c_back = st.columns([3, 5, 2])
        with c_logo:
            st.markdown(get_logo_html(), unsafe_allow_html=True)
        with c_back:
            if st.button("← Back to Home", key="back_to_landing"):
                st.session_state.current_page = "landing"
                st.rerun()
        st.markdown("<hr style='margin: 8px 0 24px 0; opacity: 0.3;'>", unsafe_allow_html=True)

        from components.auth import show_auth_page
        show_auth_page()

    else:
        # Landing page (default for unauthenticated)
        c_logo, _, c_login = st.columns([3, 5, 2])
        with c_logo:
            st.markdown(get_logo_html(), unsafe_allow_html=True)
        with c_login:
            if st.button("Sign In →", key="landing_signin"):
                st.session_state.current_page = "login"
                st.rerun()
        st.markdown("<hr style='margin: 8px 0 24px 0; opacity: 0.3;'>", unsafe_allow_html=True)

        from components.landing import show_landing_page
        show_landing_page()

    # Footer on all unauthenticated pages
    from components.footer import show_footer
    show_footer()

# ── Authenticated Workspace ──────────────────────────────────────────────
else:
    c_logo, c_nav, c_user = st.columns([2, 5, 3])
    with c_logo:
        st.markdown(get_logo_html(), unsafe_allow_html=True)
    with c_nav:
        nav_items = ["📊 Dashboard", "📁 Events", "📈 Analytics"]
        if st.session_state.user_role == "superadmin":
            nav_items.append("⚙️ Admin")

        nav_map = {
            "📊 Dashboard": "dashboard",
            "📁 Events": "events",
            "📈 Analytics": "analytics",
            "⚙️ Admin": "admin",
        }

        current_nav = None
        for label, page_key in nav_map.items():
            if st.session_state.current_page == page_key:
                current_nav = label
                break
        if current_nav is None:
            current_nav = "📊 Dashboard"

        selection = st.radio(
            "Navigation",
            nav_items,
            index=nav_items.index(current_nav) if current_nav in nav_items else 0,
            horizontal=True,
            label_visibility="collapsed",
            key="auth_header_nav"
        )
        st.session_state.current_page = nav_map.get(selection, "dashboard")

    with c_user:
        cu1, cu2 = st.columns([2.2, 1])
        with cu1:
            st.markdown(f"""
            <div style="text-align: right; padding-top: 4px;">
                <div style="font-size: 0.8rem; color: #F8FAFC; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    {st.session_state.email}
                </div>
                <div style="font-size: 0.65rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">
                    {st.session_state.user_role}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with cu2:
            if st.button("Log Out", key="header_logout", use_container_width=True):
                api_client.clear_token()
                for key in _defaults:
                    st.session_state[key] = _defaults[key]
                st.rerun()

    st.markdown("<hr style='margin: 8px 0 24px 0; opacity: 0.3;'>", unsafe_allow_html=True)

    # ── Main Content Routing ─────────────────────────────────────────────
    if st.session_state.current_event_id:
        from components.event_workspace import show_event_workspace
        show_event_workspace(st.session_state.current_event_id)

    elif st.session_state.current_page == "dashboard":
        from components.dashboard import show_dashboard
        show_dashboard()

    elif st.session_state.current_page == "events":
        from components.events import show_events_management
        show_events_management()

    elif st.session_state.current_page == "analytics":
        from components.analytics import show_analytics
        show_analytics()

    elif st.session_state.current_page == "admin":
        from components.dashboard import show_dashboard
        show_dashboard()

    else:
        from components.dashboard import show_dashboard
        show_dashboard()

    # Footer on authenticated pages
    from components.footer import show_footer
    show_footer()
