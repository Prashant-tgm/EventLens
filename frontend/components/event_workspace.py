"""
Event Workspace — Tabbed workspace view for a single event (Linear project-view style).
"""
import streamlit as st
from utils.api_client import api_client
from utils.theme import metric_card, status_badge, pipeline_stage_html


def show_event_workspace(event_id: str):
    """Render the full workspace for a given event."""

    # ── Fetch Event Details ──────────────────────────────────────────────
    try:
        event = api_client.get_event_details(event_id)
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
            <h1 style="margin: 0;">{event["name"]}</h1>
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
    tabs = st.tabs(["Overview", "Uploads", "Gallery", "Team", "Settings"])

    # ═══════════════════════════════════════════════════════════════════════
    # TAB: Overview
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[0]:
        _render_overview(event, event_id)

    # ═══════════════════════════════════════════════════════════════════════
    # TAB: Uploads
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[1]:
        _render_uploads(event_id)

    # ═══════════════════════════════════════════════════════════════════════
    # TAB: Gallery
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[2]:
        _render_gallery(event_id)

    # ═══════════════════════════════════════════════════════════════════════
    # TAB: Team
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[3]:
        _render_team(event_id)

    # ═══════════════════════════════════════════════════════════════════════
    # TAB: Settings
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[4]:
        _render_settings(event, event_id)


# ══════════════════════════════════════════════════════════════════════════
# Tab Renderers
# ══════════════════════════════════════════════════════════════════════════

def _render_overview(event: dict, event_id: str):
    """Event summary, quick actions, and guest link."""

    # Description
    desc = event.get("description", "")
    if desc:
        st.markdown(f"""
        <div class="glass-card">
            <div style="color: #94A3B8; font-size: 0.75rem; text-transform: uppercase;
                        letter-spacing: 0.05em; font-weight: 600; margin-bottom: 8px;">Description</div>
            <div style="color: #CBD5E1; font-size: 0.9rem; line-height: 1.6;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    # Quick Actions
    st.markdown("<h3>Quick Actions</h3>", unsafe_allow_html=True)
    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 24px 16px;">
            <div style="font-size: 1.5rem; margin-bottom: 8px;">📤</div>
            <div style="color: #F8FAFC; font-weight: 600; font-size: 0.85rem;">Upload Photos</div>
            <div style="color: #64748B; font-size: 0.75rem; margin-top: 4px;">
                Drag & drop to upload
            </div>
        </div>
        """, unsafe_allow_html=True)
    with qa2:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 24px 16px;">
            <div style="font-size: 1.5rem; margin-bottom: 8px;">👥</div>
            <div style="color: #F8FAFC; font-weight: 600; font-size: 0.85rem;">Invite Team</div>
            <div style="color: #64748B; font-size: 0.75rem; margin-top: 4px;">
                Add photographers
            </div>
        </div>
        """, unsafe_allow_html=True)
    with qa3:
        st.markdown(f"""
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
    search_url = f"http://localhost:8501/?event_id={event_id}"
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
            with st.spinner("Uploading to storage and triggering AI pipeline..."):
                try:
                    upload_id = api_client.upload_photos_workflow(event_id, file_mappings)
                    st.success(f"Batch uploaded! Job ID: `{upload_id}`")
                    st.info("The AI pipeline (Face Detection → Alignment → Embedding → Clustering) "
                            "has been triggered in the background.")
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    # ── Processing Pipeline Visualizer ───────────────────────────────────
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3>AI Processing Pipeline</h3>", unsafe_allow_html=True)

    stages = [
        ("📤", "Uploaded"),
        ("✅", "Validated"),
        ("👁️", "Detected"),
        ("📐", "Aligned"),
        ("🧠", "Embedded"),
        ("🔗", "Clustered"),
        ("🎉", "Completed"),
    ]

    # Show the pipeline stages (static display — will be dynamic when
    # upload status API is polled)
    st.markdown(pipeline_stage_html(stages, current_index=-1), unsafe_allow_html=True)

    st.markdown("""
    <div style="color: #475569; font-size: 0.8rem; margin-top: 8px;">
        Upload photos above to start the pipeline. Each stage processes automatically.
    </div>
    """, unsafe_allow_html=True)

    # ── Upload Status Check ──────────────────────────────────────────────
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3>Check Upload Status</h3>", unsafe_allow_html=True)

    check_upload_id = st.text_input("Enter Upload Batch ID",
                                     placeholder="e.g. abc12345-...",
                                     key=f"check_upload_{event_id}")
    if check_upload_id and st.button("Check Status", key=f"btn_check_{event_id}"):
        with st.spinner("Fetching status..."):
            try:
                status = api_client.check_upload_status(event_id, check_upload_id)
                total = status.get("total_files", 0)
                processed = status.get("processed_files", 0)
                faces = status.get("faces_extracted", 0)
                batch_status = status.get("status", "unknown")

                # Map status to pipeline stage index
                stage_map = {
                    "pending": 0, "uploading": 0, "validating": 1,
                    "detecting": 2, "aligning": 3, "embedding": 4,
                    "clustering": 5, "completed": 7, "failed": -1,
                }
                stage_idx = stage_map.get(batch_status, -1)
                st.markdown(pipeline_stage_html(stages, current_index=stage_idx),
                             unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(metric_card("📁", str(total), "Total Files"),
                                 unsafe_allow_html=True)
                with c2:
                    st.markdown(metric_card("⚙️", str(processed), "Processed"),
                                 unsafe_allow_html=True)
                with c3:
                    st.markdown(metric_card("👤", str(faces), "Faces Found"),
                                 unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Could not fetch status: {e}")


def _render_gallery(event_id: str):
    """Photo gallery placeholder — shows uploaded photos when available."""
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

    search_url = f"http://localhost:8501/?event_id={event_id}"
    st.code(search_url)
    st.markdown("""
    <div style="color: #475569; font-size: 0.8rem;">
        Share this URL or print the QR code for event attendees. They can upload a selfie
        to instantly find all their photos.
    </div>
    """, unsafe_allow_html=True)

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
