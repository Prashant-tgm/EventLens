"""
Cached API wrappers — Thin caching layer over api_client using @st.cache_data.

Purpose: Prevent redundant backend HTTP calls on every Streamlit rerun.
Each wrapper caches the API response for a tuned TTL (time-to-live).

Note: Mutation endpoints (upload, invite, login) are NOT cached.
      Polling endpoints (check_upload_status) are NOT cached.
"""
import streamlit as st
from utils.api_client import api_client


# ── Analytics (60s TTL) ──────────────────────────────────────────────────

@st.cache_data(ttl=60, show_spinner=False)
def get_owner_analytics():
    """Owner aggregate stats: events, photos, faces, searches, downloads."""
    return api_client.get_owner_analytics()


@st.cache_data(ttl=60, show_spinner=False)
def get_admin_analytics():
    """System-wide admin stats: users, events, photos, faces, searches, downloads."""
    return api_client.get_admin_analytics()


@st.cache_data(ttl=120, show_spinner=False)
def get_analytics_trends(days: int = 30):
    """Time-series trend data for charts (searches, downloads per day)."""
    return api_client.get_analytics_trends(days)


# ── Events (30s TTL) ─────────────────────────────────────────────────────

@st.cache_data(ttl=30, show_spinner=False)
def get_events():
    """List of events the current user owns or is a member of."""
    return api_client.get_events()


@st.cache_data(ttl=30, show_spinner=False)
def get_event_details(event_id: str):
    """Single event details by ID."""
    return api_client.get_event_details(event_id)


@st.cache_data(ttl=30, show_spinner=False)
def get_event_stats(event_id: str):
    """Aggregate counts: photos, batches, faces, persons, processing batches."""
    return api_client.get_event_stats(event_id)


# ── Gallery (30s TTL) ────────────────────────────────────────────────────

@st.cache_data(ttl=30, show_spinner=False)
def get_event_gallery(event_id: str, page: int = 1, limit: int = 20):
    """Paginated photo gallery for an event."""
    return api_client.get_event_gallery(event_id, page, limit)


# ── Uploads (15s TTL — shorter for near-real-time) ───────────────────────

@st.cache_data(ttl=15, show_spinner=False)
def get_event_uploads(event_id: str):
    """Upload batch history for an event."""
    return api_client.get_event_uploads(event_id)


# ── Clusters (300s TTL — expensive t-SNE, long cache) ───────────────────

@st.cache_data(ttl=300, show_spinner=False)
def get_event_clusters(event_id: str):
    """2-D t-SNE projection of face embeddings grouped by person."""
    return api_client.get_event_clusters(event_id)


# ── Cache Invalidation ──────────────────────────────────────────────────

def clear_all_caches():
    """Call after mutations (upload, invite, event create) to force refresh."""
    st.cache_data.clear()
