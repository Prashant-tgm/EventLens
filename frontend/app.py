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
    "current_page": "guest_portal",
    "current_event_id": None,
    "workspace_tab": "Overview",
}
for key, val in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Check for Guest QR Code Flow ─────────────────────────────────────────
query_params = st.query_params
event_id_param = query_params.get("event_id")


# ── Guest Portal (no sidebar, full-width) ────────────────────────────────
if not st.session_state.authenticated and (
    event_id_param or st.session_state.current_page == "guest_portal"
):
    # Minimal sidebar for guest mode
    with st.sidebar:
        st.markdown(get_logo_html(), unsafe_allow_html=True)
        st.caption("AI-Powered Photo Retrieval")
        st.divider()

        mode = st.radio(
            "Mode",
            ["🔍 Guest Finder", "🔐 Photographer Portal"],
            label_visibility="collapsed",
        )

        if mode == "🔐 Photographer Portal":
            st.session_state.current_page = "login"
            st.rerun()

    from components.guest import show_guest_portal
    show_guest_portal(event_id_param)

# ── Auth Page (not logged in, selected photographer portal) ──────────────
elif not st.session_state.authenticated:
    with st.sidebar:
        st.markdown(get_logo_html(), unsafe_allow_html=True)
        st.caption("AI-Powered Photo Retrieval")
        st.divider()

        mode = st.radio(
            "Mode",
            ["🔐 Photographer Portal", "🔍 Guest Finder"],
            label_visibility="collapsed",
        )

        if mode == "🔍 Guest Finder":
            st.session_state.current_page = "guest_portal"
            st.rerun()

    from components.auth import show_auth_page
    show_auth_page()

# ── Authenticated Workspace ──────────────────────────────────────────────
else:
    # ── Sidebar Navigation (Linear-style) ────────────────────────────────
    with st.sidebar:
        # Brand
        st.markdown(get_logo_html(), unsafe_allow_html=True)

        st.divider()

        # Navigation
        nav_items = ["📊 Dashboard", "📁 Events", "📈 Analytics"]

        # Add admin nav for superadmin
        if st.session_state.user_role == "superadmin":
            nav_items.append("⚙️ Admin")

        # Map display labels to page keys
        nav_map = {
            "📊 Dashboard": "dashboard",
            "📁 Events": "events",
            "📈 Analytics": "analytics",
            "⚙️ Admin": "admin",
        }

        # Determine current selection
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
            label_visibility="collapsed",
        )

        st.session_state.current_page = nav_map.get(selection, "dashboard")

        # If viewing event workspace, show back button
        if st.session_state.current_event_id:
            st.divider()
            st.markdown(f"""
            <div style="padding: 4px 12px; background: rgba(124,58,237,0.12);
                        border-radius: 8px; border: 1px solid rgba(124,58,237,0.2);">
                <div style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;
                            letter-spacing: 0.05em; font-weight: 600;">Active Workspace</div>
                <div style="font-size: 0.9rem; color: #F8FAFC; font-weight: 600; margin-top: 2px;">
                    {st.session_state.current_event_id}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("← Back to Events", use_container_width=True):
                st.session_state.current_event_id = None
                st.session_state.current_page = "events"
                st.rerun()

        # Spacer + user info at bottom
        st.divider()
        st.markdown(f"""
        <div style="padding: 8px 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 32px; height: 32px; border-radius: 8px;
                            background: linear-gradient(135deg, #7C3AED, #8B5CF6);
                            display: flex; align-items: center; justify-content: center;
                            color: white; font-weight: 700; font-size: 0.8rem;">
                    {st.session_state.email[0].upper() if st.session_state.email else "?"}
                </div>
                <div>
                    <div style="font-size: 0.8rem; color: #F8FAFC; font-weight: 500;">
                        {st.session_state.email}
                    </div>
                    <div style="font-size: 0.65rem; color: #64748B; text-transform: uppercase;
                                letter-spacing: 0.05em;">
                        {st.session_state.user_role}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Log Out", use_container_width=True):
            api_client.clear_token()
            for key in _defaults:
                st.session_state[key] = _defaults[key]
            st.rerun()

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
