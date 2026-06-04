"""
Guest Portal — Premium selfie-search experience with animated stages.
"""
import streamlit as st
from PIL import Image
import io
import time
import requests
from utils.api_client import api_client
from utils.theme import pipeline_stage_html


def show_guest_portal(event_id_param: str = None):
    """Full-screen guest photo retrieval experience."""

    # ── Hero Section ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-section slide-up" style="padding-top: 24px; padding-bottom: 16px;">
        <div class="hero-title">Find Your Photos</div>
        <div class="hero-subtitle">
            Upload a selfie and our AI will find all your event photos in 30 seconds.
            Powered by facial recognition technology.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Event Code Entry ─────────────────────────────────────────────────
    if not event_id_param:
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 8px;">
                <span style="color: #94A3B8; font-size: 0.85rem;">
                    Enter the event code from your invitation or QR code
                </span>
            </div>
            """, unsafe_allow_html=True)
            event_id = st.text_input("Event Code",
                                      placeholder="e.g. EVT-2026-0001",
                                      key="guest_event_code",
                                      label_visibility="collapsed")
    else:
        event_id = event_id_param

    if not event_id:
        st.markdown("""
        <div style="text-align: center; color: #475569; font-size: 0.85rem; margin-top: 24px;">
            💡 Scan the QR code at your event or ask the photographer for the event code.
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Event Info Banner ────────────────────────────────────────────────
    try:
        event_info = api_client.get_event_details(event_id)
        event_name = event_info.get("name", event_id)
        event_date = event_info.get("date", "")
        event_location = event_info.get("location", "")
    except Exception:
        event_name = event_id
        event_date = ""
        event_location = ""

    st.markdown(f"""
    <div class="glass-card fade-in" style="text-align: center; max-width: 560px; margin: 0 auto 24px auto;">
        <div style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC; margin-bottom: 6px;">
            {event_name}
        </div>
        <div style="color: #64748B; font-size: 0.85rem;">
            {"📅 " + str(event_date) + " &nbsp;·&nbsp; " if event_date else ""}
            {"📍 " + event_location if event_location else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Selfie Capture Section ───────────────────────────────────────────
    col_l, col_c, col_r = st.columns([1, 2, 1])

    with col_c:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 16px;">
            <h3 style="margin-bottom: 4px;">📸 Your Selfie</h3>
            <p style="color: #64748B; font-size: 0.8rem; margin: 0;">
                Upload a photo or use your camera
            </p>
        </div>
        """, unsafe_allow_html=True)

        selfie_option = st.radio(
            "Method",
            ["📁 Upload Photo", "📷 Use Camera"],
            horizontal=True,
            key="selfie_method",
            label_visibility="collapsed",
        )

        selfie_bytes = None

        if selfie_option == "📁 Upload Photo":
            uploaded_selfie = st.file_uploader(
                "Upload a clear selfie showing your face",
                type=["jpg", "jpeg", "png"],
                key="guest_selfie_upload",
            )
            if uploaded_selfie:
                selfie_bytes = uploaded_selfie.read()
                image = Image.open(io.BytesIO(selfie_bytes))

                # Centered preview
                st.markdown("""
                <div style="text-align: center; margin: 16px 0;">
                """, unsafe_allow_html=True)
                st.image(image, caption="Your selfie", width=200)
                st.markdown("</div>", unsafe_allow_html=True)

        else:
            camera_selfie = st.camera_input("Take a photo")
            if camera_selfie:
                selfie_bytes = camera_selfie.read()

        # ── Search Button ────────────────────────────────────────────────
        if selfie_bytes:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            if st.button("🚀 Search My Photos", use_container_width=True,
                          key="btn_search"):

                # ── Animated Search Stages ───────────────────────────────
                stages = [
                    ("🔍", "Detecting Face"),
                    ("📐", "Aligning"),
                    ("🧠", "Embedding"),
                    ("🔎", "Searching"),
                    ("📸", "Retrieving"),
                    ("✅", "Complete"),
                ]

                stage_placeholder = st.empty()
                status_text = st.empty()

                # Animate through stages
                for i in range(len(stages)):
                    stage_placeholder.markdown(
                        pipeline_stage_html(stages, current_index=i),
                        unsafe_allow_html=True,
                    )
                    status_text.markdown(f"""
                    <div style="text-align: center; color: #94A3B8; font-size: 0.85rem;">
                        {stages[i][0]} {stages[i][1]}...
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(2)

                # Perform actual search
                try:
                    search_res = api_client.search_by_selfie(event_id, selfie_bytes)

                    # Show completed pipeline
                    stage_placeholder.markdown(
                        pipeline_stage_html(stages, current_index=len(stages)),
                        unsafe_allow_html=True,
                    )
                    status_text.empty()

                    if search_res.get("success"):
                        photos = search_res.get("photos", [])

                        if not photos:
                            st.markdown("""
                            <div class="glass-card" style="text-align: center; padding: 32px;">
                                <div style="font-size: 2rem; margin-bottom: 12px;">🔍</div>
                                <div style="color: #F8FAFC; font-weight: 600; margin-bottom: 8px;">
                                    No Photos Found
                                </div>
                                <div style="color: #64748B; font-size: 0.85rem;">
                                    We couldn't find matching photos. Try another selfie with
                                    better lighting or a different angle.
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            return

                        # ── Success Banner ───────────────────────────────
                        st.markdown(f"""
                        <div class="glass-card fade-in" style="text-align: center;
                                    border-color: rgba(16,185,129,0.3); padding: 20px;">
                            <div style="font-size: 1.5rem; margin-bottom: 8px;">🎉</div>
                            <div style="color: #10B981; font-weight: 700; font-size: 1.25rem;">
                                Found {len(photos)} photos of you!
                            </div>
                            <div style="color: #64748B; font-size: 0.8rem; margin-top: 4px;">
                                Click on any photo to download it.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown("<div style='height: 16px;'></div>",
                                     unsafe_allow_html=True)

                        # ── Photo Grid (3 columns) ──────────────────────
                        cols = st.columns(3)
                        for idx, photo in enumerate(photos):
                            col = cols[idx % 3]
                            with col:
                                st.image(photo["download_url"],
                                         use_column_width=True)
                                photo_id = photo.get("photo_id", idx)
                                st.markdown(f"""
                                <a href="{photo['download_url']}" target="_blank"
                                   download="eventlens_{photo_id}.jpg"
                                   style="text-decoration: none; display: block;">
                                    <div style="background: linear-gradient(135deg, #7C3AED, #8B5CF6);
                                                color: white; text-align: center; padding: 8px;
                                                border-radius: 8px; font-size: 0.8rem;
                                                font-weight: 600; margin-bottom: 12px;
                                                transition: opacity 0.2s;">
                                        ⬇ Download
                                    </div>
                                </a>
                                """, unsafe_allow_html=True)

                    else:
                        st.error("Search failed. Please try again.")

                except requests.exceptions.HTTPError as he:
                    stage_placeholder.empty()
                    status_text.empty()
                    # Extract the user-friendly message from the backend JSON response
                    try:
                        detail = he.response.json().get("detail", str(he))
                    except Exception:
                        detail = str(he)
                    st.warning(f"⚠️ {detail}")
                except Exception as e:
                    stage_placeholder.empty()
                    status_text.empty()
                    st.error(f"Search encountered an error: {e}")

    # ── Privacy Notice ───────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align: center; margin-top: 48px; padding: 16px;">
        <p style="color: #334155; font-size: 0.7rem; max-width: 480px; margin: 0 auto;">
            🔒 Your selfie is processed securely and only used for photo matching.
            No biometric data is stored after the search is complete.
        </p>
    </div>
    """, unsafe_allow_html=True)
