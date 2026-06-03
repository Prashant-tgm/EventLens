"""
Dashboard — Linear-inspired command center with glassmorphism metric cards.
"""
import streamlit as st
from utils.api_client import api_client
from utils.theme import metric_card, status_badge
from datetime import datetime


def show_dashboard():
    role = st.session_state.get("user_role", "photographer")
    email = st.session_state.get("email", "")

    # ── Welcome Header ───────────────────────────────────────────────────
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    name = email.split("@")[0] if email else "there"

    st.markdown(f"""
    <div class="fade-in" style="margin-bottom: 32px;">
        <h1 style="margin-bottom: 4px;">{greeting}, {name}</h1>
        <p style="color: #64748B; font-size: 0.9rem; margin: 0;">
            Here's what's happening across your workspace.
            <span>{status_badge(role, "completed")}</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Admin Dashboard ──────────────────────────────────────────────────
    if role == "superadmin":
        _show_admin_dashboard()
    else:
        _show_owner_dashboard()


def _show_owner_dashboard():
    """Owner / Photographer dashboard with real metrics."""
    try:
        stats = api_client.get_owner_analytics()
    except Exception as e:
        st.error(f"Could not load analytics: {e}")
        return

    # ── Metric Cards — Row 1 ─────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(metric_card("📁", str(stats["total_events"]), "Total Events"),
                     unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("📸", str(stats["total_photos"]), "Total Photos"),
                     unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("👤", str(stats["total_faces"]), "Extracted Faces"),
                     unsafe_allow_html=True)

    # ── Metric Cards — Row 2 ─────────────────────────────────────────────
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(metric_card("🔍", str(stats["total_searches"]), "Selfie Searches"),
                     unsafe_allow_html=True)
    with c5:
        st.markdown(metric_card("⬇️", str(stats["download_count"]), "Downloads"),
                     unsafe_allow_html=True)
    with c6:
        rate = stats.get("search_success_rate", 0)
        color = "#10B981" if rate >= 80 else "#F59E0B" if rate >= 50 else "#EF4444"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-value" style="color: {color};">{rate}%</div>
            <div class="metric-label">Search Accuracy</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # ── Quick Actions ────────────────────────────────────────────────────
    st.markdown("""
    <h3 style="margin-bottom: 12px;">Quick Actions</h3>
    """, unsafe_allow_html=True)

    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        if st.button("📁 Create Event", use_container_width=True):
            st.session_state.current_page = "events"
            st.rerun()
    with qa2:
        if st.button("📈 View Analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()
    with qa3:
        if st.button("📁 Browse Events", use_container_width=True):
            st.session_state.current_page = "events"
            st.rerun()

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # ── Recent Events ────────────────────────────────────────────────────
    st.markdown("""
    <h3 style="margin-bottom: 16px;">Recent Events</h3>
    """, unsafe_allow_html=True)

    try:
        events = api_client.get_events()
        if not events:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 48px 24px;">
                <div style="font-size: 2.5rem; margin-bottom: 12px;">📁</div>
                <div style="color: #F8FAFC; font-weight: 600; font-size: 1rem; margin-bottom: 8px;">
                    No events yet
                </div>
                <div style="color: #64748B; font-size: 0.85rem;">
                    Create your first event to start uploading photos.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Show latest 4 events as cards
            cols = st.columns(2)
            for idx, event in enumerate(events[:4]):
                with cols[idx % 2]:
                    eid = event["event_id"]
                    st.markdown(f"""
                    <div class="event-card">
                        <div class="event-name">{event["name"]}</div>
                        <div class="event-meta">📅 {event.get("date", "—")} &nbsp;·&nbsp;
                            📍 {event.get("location", "—")}</div>
                        <div class="event-meta">🏷️ {event.get("event_type", "—")}</div>
                        <div class="event-stats">
                            <div class="stat-item">
                                <span class="stat-value">—</span>
                                <span class="stat-label">Photos</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">—</span>
                                <span class="stat-label">Faces</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(f"Open →", key=f"dash_open_{eid}", use_container_width=True):
                        st.session_state.current_event_id = eid
                        st.rerun()

    except Exception as e:
        st.error(f"Could not load events: {e}")


def _show_admin_dashboard():
    """System-wide admin dashboard."""
    try:
        stats = api_client.get_admin_analytics()
    except Exception as e:
        st.error(f"Could not load admin stats: {e}")
        return

    # ── System Metrics ───────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(metric_card("👥", str(stats["active_users"]), "Active Users"),
                     unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("📁", str(stats["total_events"]), "Total Events"),
                     unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("📸", str(stats["total_photos"]), "Total Photos"),
                     unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(metric_card("👤", str(stats["total_faces"]), "Faces Detected"),
                     unsafe_allow_html=True)
    with c5:
        st.markdown(metric_card("🔍", str(stats["total_searches"]), "Total Searches"),
                     unsafe_allow_html=True)
    with c6:
        st.markdown(metric_card("⬇️", str(stats["total_downloads"]), "Total Downloads"),
                     unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # ── System Status ────────────────────────────────────────────────────
    st.markdown("""
    <h3 style="margin-bottom: 12px;">System Status</h3>
    """, unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: #10B981;"></div>
                <span style="color: #F8FAFC; font-weight: 600; font-size: 0.85rem;">Database</span>
            </div>
            <div style="color: #64748B; font-size: 0.75rem;">PostgreSQL + pgvector</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: #10B981;"></div>
                <span style="color: #F8FAFC; font-weight: 600; font-size: 0.85rem;">Queue</span>
            </div>
            <div style="color: #64748B; font-size: 0.75rem;">Redis + Celery</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: #10B981;"></div>
                <span style="color: #F8FAFC; font-weight: 600; font-size: 0.85rem;">Storage</span>
            </div>
            <div style="color: #64748B; font-size: 0.75rem;">MinIO Object Storage</div>
        </div>
        """, unsafe_allow_html=True)
