"""
Events Management — Card-grid event listing and creation form.
"""
import streamlit as st
import datetime
from utils.api_client import api_client
from utils.theme import status_badge


def show_events_management():
    # ── Header ───────────────────────────────────────────────────────────
    header_col, action_col = st.columns([3, 1])
    with header_col:
        st.markdown("""
        <div class="fade-in">
            <h1 style="margin-bottom: 4px;">Events</h1>
            <p style="color: #64748B; font-size: 0.85rem; margin: 0;">
                Manage your events, upload photos, and track AI processing.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with action_col:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        show_create = st.button("+ Create Event", use_container_width=True)

    # ── Create Event Form (slide-down panel) ─────────────────────────────
    if show_create:
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        with st.expander("📁 New Event", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Event Name", placeholder="Annual Gala 2026",
                                     key="create_name")
                event_type = st.selectbox("Event Type",
                                          ["Wedding", "College Fest", "Conference",
                                           "Marathon", "Birthday", "Corporate", "Other"],
                                          key="create_type")
            with c2:
                date_val = st.date_input("Event Date", min_value=datetime.date.today(),
                                         key="create_date")
                location = st.text_input("Location", placeholder="Grand Ballroom, NYC",
                                         key="create_location")

            description = st.text_area("Description (optional)",
                                       placeholder="Brief description of the event...",
                                       key="create_desc", height=80)

            if st.button("Create Event →", key="btn_create_event", use_container_width=True):
                if not name:
                    st.error("Event name is required.")
                else:
                    with st.spinner("Creating event..."):
                        try:
                            res = api_client.create_event(
                                name=name,
                                date_str=date_val.isoformat(),
                                event_type=event_type,
                                location=location,
                                description=description,
                            )
                            st.success(f"Event created! ID: {res['event_id']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to create event: {e}")

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # ── Event Cards Grid ─────────────────────────────────────────────────
    try:
        events = api_client.get_events()
    except Exception as e:
        st.error(f"Could not load events: {e}")
        return

    if not events:
        st.markdown("""
        <div class="glass-card slide-up" style="text-align: center; padding: 64px 24px;">
            <div style="font-size: 3rem; margin-bottom: 16px;">📁</div>
            <div style="color: #F8FAFC; font-weight: 600; font-size: 1.125rem; margin-bottom: 8px;">
                No events yet
            </div>
            <div style="color: #64748B; font-size: 0.9rem; max-width: 400px; margin: 0 auto;">
                Click "Create Event" above to get started. You'll be able to upload photos,
                invite your team, and generate QR codes for guests.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Render event cards in 2-column grid
    cols = st.columns(2)
    for idx, event in enumerate(events):
        with cols[idx % 2]:
            eid = event["event_id"]
            etype = event.get("event_type", "Event")
            date_str = event.get("date", "—")
            loc = event.get("location", "—")
            desc = event.get("description", "")

            # Type to emoji mapping
            type_emoji = {
                "Wedding": "💒", "College Fest": "🎓", "Conference": "🎤",
                "Marathon": "🏃", "Birthday": "🎂", "Corporate": "💼",
            }.get(etype, "📁")

            st.markdown(f"""
            <div class="event-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div class="event-name">{type_emoji} {event["name"]}</div>
                        <div class="event-meta">📅 {date_str} &nbsp;·&nbsp; 📍 {loc}</div>
                    </div>
                    {status_badge("Active", "active")}
                </div>
                <div style="color: #64748B; font-size: 0.8rem; margin-top: 8px;
                            max-height: 40px; overflow: hidden;">
                    {desc[:100] + "..." if len(desc) > 100 else desc}
                </div>
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(148,163,184,0.12);
                            display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.7rem; color: #475569; font-family: monospace;">{eid}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Open Workspace →", key=f"open_{eid}", use_container_width=True):
                st.session_state.current_event_id = eid
                st.rerun()

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
