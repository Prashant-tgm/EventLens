"""
Analytics — Dedicated analytics page with metrics and charts.
"""
import streamlit as st
import pandas as pd
import numpy as np
from utils.api_client import api_client
from utils.theme import metric_card


def show_analytics():
    role = st.session_state.get("user_role", "photographer")

    # ── Header ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="fade-in">
        <h1 style="margin-bottom: 4px;">Analytics</h1>
        <p style="color: #64748B; font-size: 0.85rem; margin: 0;">
            Track performance metrics, search accuracy, and platform usage.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # ── Fetch Data ───────────────────────────────────────────────────────
    if role == "superadmin":
        _show_admin_analytics()
    else:
        _show_owner_analytics()


def _show_owner_analytics():
    """Owner / photographer analytics."""
    try:
        stats = api_client.get_owner_analytics()
    except Exception as e:
        st.error(f"Could not load analytics: {e}")
        return

    # ── Key Metrics ──────────────────────────────────────────────────────
    st.markdown("<h3>Key Metrics</h3>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card("📁", str(stats["total_events"]), "Events"),
                     unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("📸", str(stats["total_photos"]), "Photos"),
                     unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("👤", str(stats["total_faces"]), "Faces"),
                     unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card("📤", str(stats["total_uploads"]), "Batches"),
                     unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # ── Search Performance ───────────────────────────────────────────────
    st.markdown("<h3>Search Performance</h3>", unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(metric_card("🔍", str(stats["total_searches"]), "Total Searches"),
                     unsafe_allow_html=True)
    with s2:
        st.markdown(metric_card("✅", str(stats["successful_searches"]), "Successful"),
                     unsafe_allow_html=True)
    with s3:
        rate = stats.get("search_success_rate", 0)
        color = "#10B981" if rate >= 80 else "#F59E0B" if rate >= 50 else "#EF4444"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-value" style="color: {color};">{rate}%</div>
            <div class="metric-label">Success Rate</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # ── Download Metrics ─────────────────────────────────────────────────
    st.markdown("<h3>Downloads</h3>", unsafe_allow_html=True)

    d1, d2 = st.columns(2)
    with d1:
        st.markdown(metric_card("⬇️", str(stats["download_count"]), "Total Downloads"),
                     unsafe_allow_html=True)
    with d2:
        guests = stats.get("total_searches", 0)
        st.markdown(metric_card("👥", str(guests), "Guest Interactions"),
                     unsafe_allow_html=True)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # ── Trend Charts ─────────────────────────────────────────────────────
    st.markdown("<h3>Activity Trends</h3>", unsafe_allow_html=True)

    st.markdown("""
    <div style="color: #475569; font-size: 0.8rem; margin-bottom: 12px;">
        Simulated trend data — will use real time-series data when available.
    </div>
    """, unsafe_allow_html=True)

    chart_tabs = st.tabs(["Uploads", "Searches", "Downloads"])

    with chart_tabs[0]:
        chart_data = pd.DataFrame(
            np.random.randint(0, 50, size=(14, 1)),
            columns=["Uploads"],
            index=pd.date_range(end=pd.Timestamp.now(), periods=14, freq="D"),
        )
        st.area_chart(chart_data, color="#7C3AED")

    with chart_tabs[1]:
        chart_data = pd.DataFrame(
            np.random.randint(0, 30, size=(14, 1)),
            columns=["Searches"],
            index=pd.date_range(end=pd.Timestamp.now(), periods=14, freq="D"),
        )
        st.area_chart(chart_data, color="#10B981")

    with chart_tabs[2]:
        chart_data = pd.DataFrame(
            np.random.randint(0, 20, size=(14, 1)),
            columns=["Downloads"],
            index=pd.date_range(end=pd.Timestamp.now(), periods=14, freq="D"),
        )
        st.area_chart(chart_data, color="#F59E0B")


def _show_admin_analytics():
    """System-wide admin analytics."""
    try:
        stats = api_client.get_admin_analytics()
    except Exception as e:
        st.error(f"Could not load admin analytics: {e}")
        return

    # ── Platform Metrics ─────────────────────────────────────────────────
    st.markdown("<h3>Platform Overview</h3>", unsafe_allow_html=True)

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
        st.markdown(metric_card("🔍", str(stats["total_searches"]), "Searches"),
                     unsafe_allow_html=True)
    with c6:
        st.markdown(metric_card("⬇️", str(stats["total_downloads"]), "Downloads"),
                     unsafe_allow_html=True)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # ── Growth Chart ─────────────────────────────────────────────────────
    st.markdown("<h3>Platform Growth</h3>", unsafe_allow_html=True)

    chart_data = pd.DataFrame(
        np.random.randint(0, 100, size=(30, 3)),
        columns=["Photos", "Searches", "Downloads"],
        index=pd.date_range(end=pd.Timestamp.now(), periods=30, freq="D"),
    )
    st.line_chart(chart_data)
