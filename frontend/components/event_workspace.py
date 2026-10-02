"""
Event Workspace — Tabbed workspace view for a single event (Linear project-view style).
"""
import html
import os
import time
import streamlit as st
from utils.api_client import api_client
from utils import cached_api
from utils.theme import metric_card, status_badge, pipeline_stage_html
import plotly.express as px
# Build Plotly constellation scatter
import plotly.graph_objects as go

def show_event_workspace(event_id: str):
    """Render the full workspace for a given event."""

    # ── Fetch Event Details ──────────────────────────────────────────────
    try:
        event = cached_api.get_event_details(event_id)
    except Exception as e:
        st.error(f"Could not load event: {e}")
        return

    # ── Back Navigation ──────────────────────────────────────────────────
    col_back, _ = st.columns([1.5, 8.5])
    with col_back:
        if st.button("← Back to Events", key="btn_back_to_events", use_container_width=True):
            st.session_state.current_event_id = None
            st.session_state.current_page = "events"
            st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # ── Workspace Header ─────────────────────────────────────────────────
    etype = event.get("event_type", "Event")
    type_emoji = {
        "Wedding": "💒", "College Fest": "🎓", "Conference": "🎤",
        "Marathon": "🏃", "Birthday": "🎂", "Corporate": "💼",
    }.get(etype, "📁")

    st.markdown(f"""
    <div class="fade-in" style="margin-bottom: 8px;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <span style="font-size: 1.75rem;">{type_emoji}</span>
            <h1 style="margin: 0;">{html.escape(event["name"])}</h1>
        </div>
        <div style="display: flex; gap: 20px; flex-wrap: wrap; align-items: center;">
            <span style="color: #94A3B8; font-size: 0.85rem;">📅 {event.get("date", "—")}</span>
            <span style="color: #94A3B8; font-size: 0.85rem;">📍 {event.get("location", "—")}</span>
            <span style="color: #94A3B8; font-size: 0.85rem;">🏷️ {etype}</span>
            <span style="font-family: monospace; color: #475569; font-size: 0.75rem;
                         background: rgba(51,65,85,0.5); padding: 2px 8px; border-radius: 4px;">
                {event_id}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Workspace Tabs ───────────────────────────────────────────────────
    tabs = st.tabs(["Overview", "Uploads", "Gallery", "Clusters", "Team", "Settings"])

    with tabs[0]:
        _render_overview(event, event_id)
    with tabs[1]:
        _render_uploads(event_id)
    with tabs[2]:
        _render_gallery(event_id)
    with tabs[3]:
        _render_clusters(event_id)
    with tabs[4]:
        _render_team(event_id)
    with tabs[5]:
        _render_settings(event, event_id)


# ══════════════════════════════════════════════════════════════════════════
# Tab Renderers
# ══════════════════════════════════════════════════════════════════════════

def _render_overview(event: dict, event_id: str):
    """Event summary, quick actions, stats, and guest link."""

    # ── Live Stats Row ───────────────────────────────────────────────────
    try:
        stats = cached_api.get_event_stats(event_id)
    except Exception:
        stats = {"total_photos": 0, "total_faces": 0, "total_persons": 0,
                 "total_batches": 0, "processing_batches": 0}

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(metric_card("📷", str(stats.get("total_photos", 0)), "Photos"), unsafe_allow_html=True)
    with s2:
        st.markdown(metric_card("👤", str(stats.get("total_faces", 0)), "Faces Detected"), unsafe_allow_html=True)
    with s3:
        st.markdown(metric_card("👥", str(stats.get("total_persons", 0)), "People Clustered"), unsafe_allow_html=True)
    with s4:
        st.markdown(metric_card("📦", str(stats.get("total_batches", 0)), "Upload Batches"), unsafe_allow_html=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Description
    desc = event.get("description", "")
    if desc:
        st.markdown(f"""
        <div class="glass-card">
            <div style="color: #94A3B8; font-size: 0.75rem; text-transform: uppercase;
                        letter-spacing: 0.05em; font-weight: 600; margin-bottom: 8px;">Description</div>
            <div style="color: #CBD5E1; font-size: 0.9rem; line-height: 1.6;">{html.escape(desc)}</div>
        </div>
        """, unsafe_allow_html=True)

    # Quick Actions
    st.markdown("<h3>Quick Actions</h3>", unsafe_allow_html=True)
    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 24px 16px;">
            <div style="font-size: 1.5rem; margin-bottom: 8px;">📤</div>
            <div style="color: #F8FAFC; font-weight: 600; font-size: 0.85rem;">Upload Photos</div>
            <div style="color: #64748B; font-size: 0.75rem; margin-top: 4px;">
                Drag & drop to upload
            </div>
        </div>
        """, unsafe_allow_html=True)
    with qa2:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 24px 16px;">
            <div style="font-size: 1.5rem; margin-bottom: 8px;">👥</div>
            <div style="color: #F8FAFC; font-weight: 600; font-size: 0.85rem;">Invite Team</div>
            <div style="color: #64748B; font-size: 0.75rem; margin-top: 4px;">
                Add photographers
            </div>
        </div>
        """, unsafe_allow_html=True)
    with qa3:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 24px 16px;">
            <div style="font-size: 1.5rem; margin-bottom: 8px;">📱</div>
            <div style="color: #F8FAFC; font-weight: 600; font-size: 0.85rem;">Guest Link</div>
            <div style="color: #64748B; font-size: 0.75rem; margin-top: 4px;">
                Share with attendees
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Guest Access Link
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3>Guest Access</h3>", unsafe_allow_html=True)
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:8501")
    search_url = f"{frontend_url}/?event_id={event_id}"
    st.markdown(f"""
    <div class="glass-card">
        <div style="color: #94A3B8; font-size: 0.75rem; text-transform: uppercase;
                    letter-spacing: 0.05em; font-weight: 600; margin-bottom: 8px;">
            Shareable Link
        </div>
        <div style="background: #0F172A; border: 1px solid rgba(148,163,184,0.12);
                    border-radius: 8px; padding: 12px 16px; font-family: monospace;
                    font-size: 0.85rem; color: #8B5CF6; word-break: break-all;">
            {search_url}
        </div>
        <div style="color: #475569; font-size: 0.75rem; margin-top: 8px;">
            Share this link or generate a QR code for event attendees to find their photos.
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_uploads(event_id: str):
    """Upload area + processing tracker + upload history."""

    # ── Upload Area ──────────────────────────────────────────────────────
    st.markdown("<h3>Upload Photos</h3>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drag and drop JPG/PNG photos for batch upload",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key=f"ws_upload_{event_id}",
    )

    if uploaded_files:
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #F8FAFC; font-weight: 600;">{len(uploaded_files)} files selected</span>
                    <span style="color: #64748B; font-size: 0.8rem; margin-left: 8px;">
                        Ready to upload
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📤 Upload & Start AI Pipeline", key="btn_upload_ws",
                      use_container_width=True):
            file_mappings = {f.name: f.read() for f in uploaded_files}

            # Progress tracking containers
            upload_status = st.empty()
            upload_progress = st.progress(0.0)

            def update_upload_progress(current, total):
                pct = current / total
                upload_progress.progress(pct)
                upload_status.markdown(f"📤 **Uploading to Storage:** {current} of {total} files ({int(pct * 100)}%)")

            try:
                upload_id = api_client.upload_photos_workflow(
                    event_id, file_mappings, progress_callback=update_upload_progress
                )
                upload_status.success(f"🎉 Upload complete! Job ID: `{upload_id}`")
                st.session_state["active_upload_id"] = upload_id
                st.session_state["active_upload_total"] = len(uploaded_files)
                cached_api.clear_all_caches()
                st.rerun()
            except Exception as e:
                st.error(f"Upload failed: {e}")

    # ── Active Processing Monitor ───────────────────────────────────────
    stages = [
        ("📤", "Uploaded"),
        ("✅", "Validated"),
        ("👁️", "Detected"),
        ("📐", "Aligned"),
        ("🧠", "Embedded"),
        ("🔗", "Clustered"),
        ("🎉", "Completed"),
    ]

    active_upload_id = st.session_state.get("active_upload_id")
    if active_upload_id:
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card fade-in" style="border-color: rgba(139, 92, 246, 0.4); padding: 20px; border-radius: 8px;">
            <div style="color: #8B5CF6; font-weight: 700; margin-bottom: 12px; font-size: 1rem;">
                ⚙️ AI Processing Pipeline Progress
            </div>
        """, unsafe_allow_html=True)

        status_text = st.empty()
        ai_progress = st.progress(0.0)
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        stage_viz = st.empty()

        with st.spinner("AI Processing..."):
            while True:
                try:
                    status_data = api_client.check_upload_status(event_id, active_upload_id)
                    total = status_data.get("total_files", 0) or st.session_state.get("active_upload_total", 1)
                    processed = status_data.get("processed_files", 0)
                    faces = status_data.get("faces_extracted", 0)
                    batch_status = status_data.get("status", "pending")

                    if total > 0:
                        pct = min(1.0, processed / total)
                        ai_progress.progress(pct)

                    status_text.markdown(f"""
                    **Batch Status:** `{batch_status.upper()}` &nbsp;·&nbsp;
                    **Processed Files:** `{processed} of {total}` &nbsp;·&nbsp;
                    **Faces Found:** `{faces}`
                    """)

                    # Map status to pipeline stage index
                    stage_map = {
                        "pending": 0, "uploading": 0, "validating": 1,
                        "processing": 2, "clustering": 5, "completed": 7, "failed": -1,
                    }
                    stage_idx = stage_map.get(batch_status, -1)
                    stage_viz.markdown(pipeline_stage_html(stages, current_index=stage_idx), unsafe_allow_html=True)

                    if batch_status in ("completed", "failed"):
                        if batch_status == "completed":
                            st.success("🎉 All photos successfully processed and clustered!")
                        else:
                            st.error("❌ Pipeline execution failed in background worker.")
                        del st.session_state["active_upload_id"]
                        if "active_upload_total" in st.session_state:
                            del st.session_state["active_upload_total"]
                        break

                    time.sleep(1.5)
                except Exception as e:
                    st.error(f"Error tracking progress: {e}")
                    break
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Processing Pipeline Visualizer ───────────────────────────────────
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3>AI Processing Pipeline</h3>", unsafe_allow_html=True)

    st.markdown(pipeline_stage_html(stages, current_index=-1), unsafe_allow_html=True)

    st.markdown("""
    <div style="color: #475569; font-size: 0.8rem; margin-top: 8px;">
        Upload photos above to start the pipeline. Each stage processes automatically.
    </div>
    """, unsafe_allow_html=True)

    # ── Upload History with Progress Bars ─────────────────────────────────
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3>Upload Batches & Progress</h3>", unsafe_allow_html=True)

    try:
        uploads_history = cached_api.get_event_uploads(event_id)
        if uploads_history:
            for u in uploads_history:
                uid = u["upload_id"]
                batch_status = u["status"].upper()
                total_files = u.get("total_files", 0) or 1
                processed_files = u.get("processed_files", 0)
                faces_found = u.get("faces_extracted", 0)
                created_at = u.get("created_at", "")[:19] if u.get("created_at") else "—"
                progress_pct = min(1.0, processed_files / total_files) if total_files > 0 else 0.0

                # Status color
                status_color = {
                    "COMPLETED": "#10B981", "PROCESSING": "#F59E0B",
                    "PENDING": "#8B5CF6", "FAILED": "#EF4444",
                }.get(batch_status, "#64748B")

                st.markdown(f"""
                <div class="glass-card" style="padding: 16px 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div>
                            <span style="font-family: monospace; color: #8B5CF6; font-size: 0.8rem;">
                                {uid[:8]}…
                            </span>
                            <span style="color: #64748B; font-size: 0.75rem; margin-left: 8px;">
                                {created_at}
                            </span>
                        </div>
                        <span style="font-size: 0.7rem; font-weight: 700; color: {status_color};
                                     padding: 2px 10px; border-radius: 12px;
                                     background: rgba({",".join(str(int(status_color.lstrip("#")[i:i+2], 16)) for i in (0, 2, 4))}, 0.15);">
                            {batch_status}
                        </span>
                    </div>
                    <div style="display: flex; gap: 24px; font-size: 0.8rem; color: #94A3B8; margin-bottom: 8px;">
                        <span>📷 {processed_files}/{total_files} files</span>
                        <span>👤 {faces_found} faces</span>
                        <span>{int(progress_pct * 100)}% complete</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Streamlit native progress bar per batch
                st.progress(progress_pct)
                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        else:
            st.info("No upload batches recorded for this event yet.")
    except Exception as e:
        st.error(f"Could not load upload history: {e}")


def _render_gallery(event_id: str):
    """Photo gallery — shows uploaded and processed photos."""
    st.markdown("<h3>Photo Gallery</h3>", unsafe_allow_html=True)

    try:
        # Pre-calculate total photos
        gallery_init = cached_api.get_event_gallery(event_id, page=1, limit=1)
        total = gallery_init.get("total", 0)

        if total == 0:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 48px 24px;">
                <div style="font-size: 2.5rem; margin-bottom: 12px;">🖼️</div>
                <div style="color: #F8FAFC; font-weight: 600; font-size: 1rem; margin-bottom: 8px;">
                    No Photos Yet
                </div>
                <div style="color: #64748B; font-size: 0.85rem; max-width: 400px; margin: 0 auto;">
                    Upload photos in the Uploads tab to get started. They'll appear here
                    once processed through the AI pipeline.
                </div>
            </div>
            """, unsafe_allow_html=True)
            return

        # Pagination parameters
        limit = 40
        total_pages = max(1, (total + limit - 1) // limit)
        page_key = f"gallery_page_{event_id}"
        if page_key not in st.session_state:
            st.session_state[page_key] = 1

        current_page = st.session_state[page_key]
        if current_page > total_pages:
            current_page = total_pages
            st.session_state[page_key] = total_pages

        gallery = cached_api.get_event_gallery(event_id, page=current_page, limit=limit)
        photos = gallery.get("photos", [])

        st.markdown(f"""
        <div style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 16px;">
            Showing {len(photos)} of {total} photos (Page {current_page} of {total_pages})
        </div>
        """, unsafe_allow_html=True)

        # Display photos in a 4-column grid
        cols = st.columns(4)
        for idx, photo in enumerate(photos):
            with cols[idx % 4]:
                st.markdown(
                    f'<img src="{photo["download_url"]}" style="width:100%; border-radius:8px; margin-bottom:8px;">',
                    unsafe_allow_html=True,
                )
                st.markdown(f"""
                <div style="text-align: center; color: #64748B; font-size: 0.7rem; margin-bottom: 12px;">
                    ID: {photo['photo_id']}
                </div>
                """, unsafe_allow_html=True)

        # Pagination controls
        if total_pages > 1:
            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
            col_prev, col_page, col_next = st.columns([1, 2, 1])
            with col_prev:
                if st.button("⬅️ Previous", disabled=(current_page == 1), key=f"gal_prev_{event_id}"):
                    st.session_state[page_key] -= 1
                    st.rerun()
            with col_page:
                st.markdown(f"<div style='text-align: center; color: #94A3B8; padding-top: 8px;'>Page {current_page} of {total_pages}</div>", unsafe_allow_html=True)
            with col_next:
                if st.button("Next ➡️", disabled=(current_page == total_pages), key=f"gal_next_{event_id}"):
                    st.session_state[page_key] += 1
                    st.rerun()

    except Exception:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 48px 24px;">
            <div style="font-size: 2.5rem; margin-bottom: 12px;">🖼️</div>
            <div style="color: #F8FAFC; font-weight: 600; font-size: 1rem; margin-bottom: 8px;">
                Photo Gallery
            </div>
            <div style="color: #64748B; font-size: 0.85rem; max-width: 400px; margin: 0 auto;">
                Photos will appear here once they've been uploaded and processed through the
                AI pipeline. Upload photos in the Uploads tab to get started.
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_clusters(event_id: str):
    """Face cluster visualization — star constellation style scatter plot."""
    st.markdown("<h3>Face Clusters — Constellation View</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div style="color: #64748B; font-size: 0.85rem; margin-bottom: 16px;">
        Each dot represents a detected face. Faces clustered as the same person share a color.
        Unclustered faces appear as gray dots.
    </div>
    """, unsafe_allow_html=True)

    try:
        cluster_data = cached_api.get_event_clusters(event_id)
    except Exception as e:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 48px 24px;">
            <div style="font-size: 2.5rem; margin-bottom: 12px;">🌌</div>
            <div style="color: #F8FAFC; font-weight: 600; font-size: 1rem; margin-bottom: 8px;">
                No Cluster Data Yet
            </div>
            <div style="color: #64748B; font-size: 0.85rem; max-width: 400px; margin: 0 auto;">
                Upload and process photos to see face clusters appear here.
                The AI pipeline needs at least 2 faces to form clusters.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    total_faces = cluster_data.get("total_faces", 0)
    total_persons = cluster_data.get("total_persons", 0)
    persons = cluster_data.get("persons", [])
    unclustered = cluster_data.get("unclustered", [])

    if total_faces < 2:
        st.info("Need at least 2 detected faces to generate cluster visualization.")
        return

    # Stats row
    cs1, cs2, cs3 = st.columns(3)
    with cs1:
        st.markdown(metric_card("👤", str(total_faces), "Total Faces"), unsafe_allow_html=True)
    with cs2:
        st.markdown(metric_card("👥", str(total_persons), "People Found"), unsafe_allow_html=True)
    with cs3:
        st.markdown(metric_card("❓", str(len(unclustered)), "Unclustered"), unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    

    # Color palette for clusters (vibrant, distinct)
    cluster_colors = [
        "#8B5CF6", "#10B981", "#F59E0B", "#EF4444", "#06B6D4",
        "#EC4899", "#84CC16", "#F97316", "#6366F1", "#14B8A6",
        "#E879F9", "#FCD34D", "#FB7185", "#38BDF8", "#A3E635",
        "#C084FC", "#34D399", "#FBBF24", "#F87171", "#22D3EE",
    ]

    fig = go.Figure()

    # Plot each person cluster
    for idx, person in enumerate(persons):
        color = cluster_colors[idx % len(cluster_colors)]
        faces = person.get("faces", [])
        if not faces:
            continue

        xs = [f["x"] for f in faces]
        ys = [f["y"] for f in faces]
        photo_ids = [f"Photo #{f['photo_id']}" for f in faces]
        qualities = [f.get("quality", 0) for f in faces]

        # Size by quality (bigger = better quality face)
        sizes = [max(8, min(20, q / 5)) for q in qualities]

        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="markers",
            marker=dict(
                size=sizes,
                color=color,
                line=dict(width=1, color="rgba(255,255,255,0.3)"),
                opacity=0.85,
            ),
            name=f"👤 {person['name']} ({len(faces)})",
            text=[f"{person['name']}<br>{pid}<br>Quality: {q:.0f}" for pid, q in zip(photo_ids, qualities)],
            hoverinfo="text",
        ))

        # Draw convex hull lines connecting cluster members
        if len(faces) >= 3:
            # Simple convex hull approximation: connect centroid to each point
            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)
            for x, y in zip(xs, ys):
                fig.add_trace(go.Scatter(
                    x=[cx, x], y=[cy, y],
                    mode="lines",
                    line=dict(color=color, width=0.5, dash="dot"),
                    opacity=0.2,
                    showlegend=False,
                    hoverinfo="skip",
                ))

    # Plot unclustered faces
    if unclustered:
        xs = [f["x"] for f in unclustered]
        ys = [f["y"] for f in unclustered]
        photo_ids = [f"Photo #{f['photo_id']}" for f in unclustered]

        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="markers",
            marker=dict(
                size=6,
                color="#475569",
                line=dict(width=1, color="rgba(100,116,139,0.4)"),
                opacity=0.5,
            ),
            name=f"❓ Unclustered ({len(unclustered)})",
            text=[f"Unclustered<br>{pid}" for pid in photo_ids],
            hoverinfo="text",
        ))

    # Dark space theme
    fig.update_layout(
        plot_bgcolor="#0A0F1E",
        paper_bgcolor="#0F172A",
        font=dict(family="Inter", color="#94A3B8"),
        title=dict(
            text="Face Embedding Space — t-SNE Projection",
            font=dict(size=14, color="#F8FAFC"),
        ),
        legend=dict(
            bgcolor="rgba(15,23,42,0.8)",
            bordercolor="rgba(148,163,184,0.12)",
            borderwidth=1,
            font=dict(size=11, color="#94A3B8"),
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(51,65,85,0.3)",
            zeroline=False,
            showticklabels=False,
            title="",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(51,65,85,0.3)",
            zeroline=False,
            showticklabels=False,
            title="",
        ),
        margin=dict(l=20, r=20, t=50, b=20),
        height=550,
    )

    st.plotly_chart(fig, use_container_width=True, key=f"cluster_plot_{event_id}")

    # Person breakdown table
    if persons:
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("<h3>Person Breakdown</h3>", unsafe_allow_html=True)

        import pandas as pd
        person_rows = []
        for p in persons:
            unique_photos = len(set(f["photo_id"] for f in p.get("faces", [])))
            person_rows.append({
                "Person": p["name"],
                "Faces": p["face_count"],
                "Unique Photos": unique_photos,
            })
        df = pd.DataFrame(person_rows)
        st.dataframe(df, use_container_width=True, hide_index=True)


def _render_team(event_id: str):
    """Team management — invite photographers."""
    st.markdown("<h3>Team Members</h3>", unsafe_allow_html=True)

    # Invite form
    st.markdown("""
    <div style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 16px;">
        Invite photographers to help upload photos for this event.
    </div>
    """, unsafe_allow_html=True)

    invite_col, role_col = st.columns([3, 1])
    with invite_col:
        invite_email = st.text_input("Email address",
                                      placeholder="photographer@studio.com",
                                      key=f"invite_email_{event_id}",
                                      label_visibility="collapsed")
    with role_col:
        invite_role = st.selectbox("Role", ["Photographer", "Editor"],
                                    key=f"invite_role_{event_id}",
                                    label_visibility="collapsed")

    if st.button("Send Invitation", key=f"btn_invite_{event_id}"):
        if not invite_email:
            st.error("Please enter an email address.")
        else:
            with st.spinner("Sending invitation..."):
                try:
                    api_client.invite_member(event_id, invite_email,
                                             invite_role.lower())
                    st.success(f"Invitation sent to {invite_email}!")
                except Exception as e:
                    st.error(f"Failed to send invitation: {e}")

    # Team list placeholder
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 32px 24px;">
        <div style="font-size: 1.5rem; margin-bottom: 8px;">👥</div>
        <div style="color: #94A3B8; font-size: 0.85rem;">
            Team members will appear here once they accept their invitations.
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_settings(event: dict, event_id: str):
    """Event settings — guest link, QR, and event info."""
    st.markdown("<h3>Event Configuration</h3>", unsafe_allow_html=True)

    # Event Info
    st.markdown(f"""
    <div class="glass-card">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
            <div>
                <div style="color: #64748B; font-size: 0.7rem; text-transform: uppercase;
                            letter-spacing: 0.05em; font-weight: 600; margin-bottom: 4px;">
                    Event ID
                </div>
                <div style="color: #F8FAFC; font-size: 0.9rem; font-family: monospace;">
                    {event_id}
                </div>
            </div>
            <div>
                <div style="color: #64748B; font-size: 0.7rem; text-transform: uppercase;
                            letter-spacing: 0.05em; font-weight: 600; margin-bottom: 4px;">
                    Event Type
                </div>
                <div style="color: #F8FAFC; font-size: 0.9rem;">
                    {event.get("event_type", "—")}
                </div>
            </div>
            <div>
                <div style="color: #64748B; font-size: 0.7rem; text-transform: uppercase;
                            letter-spacing: 0.05em; font-weight: 600; margin-bottom: 4px;">
                    Date
                </div>
                <div style="color: #F8FAFC; font-size: 0.9rem;">
                    {event.get("date", "—")}
                </div>
            </div>
            <div>
                <div style="color: #64748B; font-size: 0.7rem; text-transform: uppercase;
                            letter-spacing: 0.05em; font-weight: 600; margin-bottom: 4px;">
                    Location
                </div>
                <div style="color: #F8FAFC; font-size: 0.9rem;">
                    {event.get("location", "—")}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Guest Link Section
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3>Guest Access Link</h3>", unsafe_allow_html=True)

    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:8501")
    search_url = f"{frontend_url}/?event_id={event_id}"

    col_link, col_qr = st.columns([3, 2])
    with col_link:
        st.code(search_url)
        st.markdown("""
        <div style="color: #475569; font-size: 0.8rem; margin-bottom: 16px;">
            Share this URL or print the QR code for event attendees. They can scan it to instantly upload a selfie
            and find all their photos.
        </div>
        """, unsafe_allow_html=True)

        generate_qr = st.button("📸 Generate QR Code", key=f"gen_qr_{event_id}", use_container_width=True)

    with col_qr:
        if generate_qr or st.session_state.get(f"show_qr_{event_id}", False):
            st.session_state[f"show_qr_{event_id}"] = True

            import qrcode
            import io

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(search_url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()

            # Display QR code nicely framed
            st.markdown("""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;
                        background: white; padding: 12px; border-radius: 8px; width: 174px; margin: 0 auto 12px;">
            """, unsafe_allow_html=True)
            st.image(byte_im, width=150)
            st.markdown("</div>", unsafe_allow_html=True)

            st.download_button(
                label="📥 Download QR Image",
                data=byte_im,
                file_name=f"event_{event_id}_qr.png",
                mime="image/png",
                use_container_width=True,
                key=f"dl_qr_{event_id}"
            )

    # Danger Zone
    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <h3 style="color: #EF4444 !important;">Danger Zone</h3>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-card" style="border-color: rgba(239,68,68,0.2);">
        <div style="color: #F8FAFC; font-weight: 600; font-size: 0.9rem; margin-bottom: 4px;">
            Delete Event
        </div>
        <div style="color: #64748B; font-size: 0.8rem;">
            This action is irreversible. All photos, face data, and analytics will be permanently removed.
        </div>
    </div>
    """, unsafe_allow_html=True)
