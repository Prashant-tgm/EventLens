"""
EventLens AI — Premium Landing Page.
Full-width hero, feature showcase, how-it-works, stats,
testimonial highlights, and CTA — all rendered via Streamlit components.
"""
import streamlit as st
from utils.theme import get_logo_base64, COLORS


def show_landing_page():
    """Render the complete landing page for unauthenticated users."""

    logo_b64 = get_logo_base64()
    c = COLORS

    # ── Inject landing-page-specific CSS ─────────────────────────────────
    st.markdown(_landing_css(c), unsafe_allow_html=True)

    # ── Hero Section ─────────────────────────────────────────────────────
    logo_img_html = ""
    if logo_b64:
        logo_img_html = (
            f'<img src="data:image/png;base64,{logo_b64}" '
            f'class="landing-hero-logo" alt="EventLens" />'
        )

    st.markdown(f"""
    <div class="landing-hero">
        <div class="landing-hero-glow"></div>
        <div class="landing-hero-grid-bg"></div>
        <div class="landing-hero-content slide-up">
            <h1 class="landing-hero-title">
                Every Face.<br/>Own Photo.<br/>
                <span class="landing-gradient-text">Instantly Found.</span>
            </h1>
            <div class="landing-hero-desc">
                EventLens uses cutting-edge facial recognition to match guests
                with their event photos in under <strong style="color:#F8FAFC;">10&nbsp;seconds</strong>.
                Upload once. Let AI do the rest.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CTA Buttons (native Streamlit) ───────────────────────────────────
    _s1, btn_col1, btn_col2, _s2 = st.columns([2, 1.5, 1.5, 2])
    with btn_col1:
        if st.button("Get Started Free  →", key="hero_cta_start",
                      use_container_width=True):
            st.session_state.current_page = "login"
            st.rerun()
    with btn_col2:
        st.markdown("""
        <div style="text-align:center; padding:10px 0; color:#94A3B8;
                    font-size:0.85rem; font-weight:500; cursor:default;">
            &darr; &nbsp;See How It Works
        </div>
        """, unsafe_allow_html=True)

    # ── Hero Stats Row ───────────────────────────────────────────────────
    st.markdown(f"""
    <div class="landing-hero-stats-row">
        <div class="landing-hero-stat">
            <span class="landing-hero-stat-value">10s</span>
            <span class="landing-hero-stat-label">Avg. Search Time</span>
        </div>
        <div class="landing-hero-stat-divider"></div>
        <div class="landing-hero-stat">
            <span class="landing-hero-stat-value">95%</span>
            <span class="landing-hero-stat-label">Face Match Accuracy</span>
        </div>
        <div class="landing-hero-stat-divider"></div>
        <div class="landing-hero-stat">
            <span class="landing-hero-stat-value">...</span>
            <span class="landing-hero-stat-label">Photos Processed</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Trusted By ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="landing-section" style="padding-top: 32px; padding-bottom: 24px;">
        <div class="landing-trusted-label">WANT TO MAKE A TRUST</div>
        <div class="landing-logo-bar">
            <span>StudioPro</span>
            <span>EventCo</span>
            <span>WeddingLens</span>
            <span>CorpEvents</span>
            <span>GradSnap</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Features Section ─────────────────────────────────────────────────
    st.markdown(f"""
    <div class="landing-section-header" style="padding-top:48px;">
        <div class="landing-section-tag">FEATURES</div>
        <div class="landing-section-title">
            Everything you need to<br/>
            <span class="landing-gradient-text">deliver photos at scale</span>
        </div>
        <div class="landing-section-subtitle">
            From upload to delivery, EventLens handles the entire pipeline
            so you can focus on capturing the moment.
        </div>
    </div>
    """, unsafe_allow_html=True)

    features = [
        ("\u26A1", "personal Search",
         "Guests upload a selfie and find every photo of themselves "
         "in under 10 seconds using pgvector cosine similarity.",
         "#7C3AED"),
        ("\U0001F9E0", "AI Face Clustering",
         "DBSCAN clusters faces across thousands of photos so each "
         "person's gallery is built automatically.",
         "#3B82F6"),
        ("\U0001F512", "Event-Isolated Security",
         "Strict multi-tenant isolation guarantees zero cross-event "
         "face leakage. Biometric data is never stored after search.",
         "#10B981"),
        ("\U0001F4F1", "QR Code Guest Portal",
         "Generate a unique QR code per event. Guests scan, snap a "
         "selfie, and download their photos in a cleaner way.",
         "#F59E0B"),
        ("\u2601\uFE0F", "Cloud-Native Pipeline",
         "Direct-to-S3 uploads via pre-signed URLs. Celery workers "
         "process 128-photo batches with RetinaFace + ArcFace.",
         "#EC4899"),
        ("\U0001F4CA", "Real-Time Analytics",
         "Track upload progress, face detection rates, search volume, "
         "and guest engagement from your organizer dashboard.",
         "#06B6D4"),
    ]

    # Render feature cards using st.columns (3 per row)
    row1 = st.columns(3)
    row2 = st.columns(3)
    all_cols = row1 + row2
    for i, (icon, title, desc, accent) in enumerate(features):
        with all_cols[i]:
            st.markdown(f"""
            <div class="landing-feature-card">
                <div class="landing-feature-icon"
                     style="background:{accent}22;color:{accent};">{icon}</div>
                <div class="landing-feature-title">{title}</div>
                <div class="landing-feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── How It Works Section ─────────────────────────────────────────────
    st.markdown(f"""
    <div class="landing-section-alt-bg">
        <div class="landing-section-header">
            <div class="landing-section-tag">HOW IT WORKS</div>
            <div class="landing-section-title">
                Four steps to<br/>
                <span class="landing-gradient-text">photo magic</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    steps = [
        ("01", "\U0001F4E4", "Upload Event Photos",
         "Photographers bulk-upload directly to cloud storage via "
         "pre-signed URLs. No size limits, no bottlenecks."),
        ("02", "\U0001F9EC", "AI Processes Faces",
         "RetinaFace detects faces, ArcFace generates 512-D embeddings, "
         "and DBSCAN clusters them automatically."),
        ("03", "\U0001F4F1", "Share QR Code",
         "Generate a unique event QR code. Guests scan it from "
         "their phone. No downloads, no signups."),
        ("04", "\U0001F389", "Guests Get Photos",
         "One selfie. Every matching photo is ready to "
         "download in original quality."),
    ]

    step_cols = st.columns(4)
    for i, (num, icon, title, desc) in enumerate(steps):
        with step_cols[i]:
            st.markdown(f"""
            <div class="landing-step">
                <div class="landing-step-num">{num}</div>
                <div class="landing-step-icon">{icon}</div>
                <div class="landing-step-title">{title}</div>
                <div class="landing-step-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # # ── Testimonials Section ─────────────────────────────────────────────
    # st.markdown(f"""
    # <div class="landing-section-header" style="padding-top:56px;">
    #     <div class="landing-section-tag">TESTIMONIALS</div>
    #     <div class="landing-section-title">
    #         Loved by<br/>
    #         <span class="landing-gradient-text">event professionals</span>
    #     </div>
    # </div>
    # """, unsafe_allow_html=True)

    # testimonials = [
    #     ("EventLens saved us 12+ hours of manual photo sorting at "
    #      "a 500-guest corporate gala. Guests loved the instant delivery.",
    #      "Sarah K.", "Event Director, CorpEvents"),
    #     ("The QR code flow is genius. Guests pull out their phone, "
    #      "snap a selfie, and have all their photos in seconds. Pure magic.",
    #      "James M.", "Lead Photographer, StudioPro"),
    #     ("We process thousands of wedding photos. The AI clustering "
    #      "is incredibly accurate, even with varied lighting conditions.",
    #      "Priya R.", "Founder, WeddingLens"),
    # ]

    # t_cols = st.columns(3)
    # for i, (quote, author, role) in enumerate(testimonials):
    #     with t_cols[i]:
    #         st.markdown(f"""
    #         <div class="landing-testimonial-card">
    #             <div class="landing-testimonial-stars">\u2605\u2605\u2605\u2605\u2605</div>
    #             <div class="landing-testimonial-quote">&ldquo;{quote}&rdquo;</div>
    #             <div class="landing-testimonial-author">
    #                 <div>
    #                     <div class="landing-testimonial-name">{author}</div>
    #                     <div class="landing-testimonial-role">{role}</div>
    #                 </div>
    #             </div>
    #         </div>
    #         """, unsafe_allow_html=True)

    # ── Final CTA Section ────────────────────────────────────────────────
    st.markdown(f"""
    <div class="landing-cta-section">
        <div class="landing-cta-glow"></div>
        <div class="landing-cta-content">
            <div class="landing-cta-title">
                Ready to transform your<br/>event photo delivery?
            </div>
            <div class="landing-cta-desc">
                Start for free. No credit card required.
                Set up your first event in under 5 minutes.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _sl, cta_col, _sr = st.columns([1, 2, 1])
    with cta_col:
        if st.button("\U0001F680  Create Your Free Account", key="landing_cta_btn",
                      use_container_width=True):
            st.session_state.current_page = "login"
            st.rerun()


# ═════════════════════════════════════════════════════════════════════════
# Landing-specific CSS
# ═════════════════════════════════════════════════════════════════════════

def _landing_css(c: dict) -> str:
    return f"""<style>
.landing-hero {{
    position: relative;
    text-align: center;
    padding: 60px 24px 20px;
    overflow: hidden;
}}
.landing-hero-glow {{
    position: absolute;
    top: -120px; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 600px;
    background: radial-gradient(circle, {c['accent_glow']}, transparent 70%);
    pointer-events: none;
    z-index: 0;
}}
.landing-hero-grid-bg {{
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient({c['border']} 1px, transparent 1px),
        linear-gradient(90deg, {c['border']} 1px, transparent 1px);
    background-size: 64px 64px;
    opacity: 0.35;
    mask-image: radial-gradient(ellipse 60% 50% at 50% 0%, black, transparent);
    -webkit-mask-image: radial-gradient(ellipse 60% 50% at 50% 0%, black, transparent);
    pointer-events: none;
    z-index: 0;
}}
.landing-hero-content {{
    position: relative;
    z-index: 1;
    max-width: 720px;
    margin: 0 auto;
}}
.landing-hero-logo {{
    height: 64px; width: 64px;
    object-fit: contain;
    border-radius: 14px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(124,58,237,0.25);
}}
.landing-hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: {c['bg_secondary']};
    border: 1px solid {c['border']};
    border-radius: 999px;
    padding: 6px 18px;
    font-size: 0.75rem;
    color: {c['text_muted']};
    font-weight: 500;
    letter-spacing: 0.03em;
    margin-bottom: 28px;
}}
.landing-badge-dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    background: {c['success']};
    box-shadow: 0 0 8px {c['success']};
    animation: pulse 2s infinite;
    display: inline-block;
}}
.landing-hero-title {{
    font-size: 3.5rem !important;
    font-weight: 800 !important;
    line-height: 1.1 !important;
    letter-spacing: -0.04em;
    color: {c['text_primary']} !important;
    margin-bottom: 20px !important;
}}
.landing-gradient-text {{
    background: linear-gradient(135deg, {c['accent']}, {c['accent_light']}, #a78bfa, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.landing-hero-desc {{
    font-size: 1.125rem;
    color: {c['text_dim']};
    line-height: 1.7;
    max-width: 540px;
    margin: 0 auto 32px;
}}
.landing-hero-stats-row {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 32px;
    flex-wrap: wrap;
    margin-bottom: 32px;
}}
.landing-hero-stat {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}}
.landing-hero-stat-value {{
    font-size: 1.75rem;
    font-weight: 800;
    color: {c['text_primary']};
    letter-spacing: -0.02em;
}}
.landing-hero-stat-label {{
    font-size: 0.7rem;
    color: {c['text_dim']};
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
}}
.landing-hero-stat-divider {{
    width: 1px; height: 40px;
    background: {c['border']};
}}
.landing-section {{
    padding: 64px 24px;
    max-width: 1100px;
    margin: 0 auto;
}}
.landing-section-alt-bg {{
    background: {c['bg_secondary']};
    border-radius: 24px;
    margin: 32px auto;
    max-width: 1100px;
    border: 1px solid {c['glass_border']};
    padding: 48px 24px 8px;
}}
.landing-section-header {{
    text-align: center;
    margin-bottom: 32px;
}}
.landing-section-tag {{
    font-size: 0.7rem;
    color: {c['accent_light']};
    letter-spacing: 0.12em;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 12px;
}}
.landing-section-title {{
    font-size: 2.25rem;
    font-weight: 800;
    color: {c['text_primary']};
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 12px;
}}
.landing-section-subtitle {{
    font-size: 1rem;
    color: {c['text_dim']};
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.6;
}}
.landing-trusted-label {{
    text-align: center;
    font-size: 0.65rem;
    color: {c['text_dim']};
    letter-spacing: 0.14em;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 20px;
}}
.landing-logo-bar {{
    display: flex;
    justify-content: center;
    gap: 40px;
    flex-wrap: wrap;
    color: {c['text_dim']};
    font-size: 0.9rem;
    font-weight: 500;
    opacity: 0.55;
}}
.landing-feature-card {{
    background: {c['glass_bg']};
    border: 1px solid {c['glass_border']};
    border-radius: 16px;
    padding: 28px 24px;
    transition: all 0.25s ease;
    backdrop-filter: blur(12px);
    margin-bottom: 16px;
}}
.landing-feature-card:hover {{
    border-color: {c['border_hover']};
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.25);
}}
.landing-feature-icon {{
    width: 48px; height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    margin-bottom: 16px;
}}
.landing-feature-title {{
    font-size: 1.05rem;
    font-weight: 700;
    color: {c['text_primary']};
    margin-bottom: 8px;
}}
.landing-feature-desc {{
    font-size: 0.85rem;
    color: {c['text_dim']};
    line-height: 1.6;
}}
.landing-step {{
    text-align: center;
    padding: 16px 8px;
}}
.landing-step-num {{
    font-size: 0.7rem;
    font-weight: 800;
    color: {c['accent_light']};
    letter-spacing: 0.08em;
    margin-bottom: 12px;
}}
.landing-step-icon {{
    font-size: 2rem;
    margin-bottom: 12px;
}}
.landing-step-title {{
    font-size: 1rem;
    font-weight: 700;
    color: {c['text_primary']};
    margin-bottom: 6px;
}}
.landing-step-desc {{
    font-size: 0.8rem;
    color: {c['text_dim']};
    line-height: 1.6;
}}
.landing-testimonial-card {{
    background: {c['glass_bg']};
    border: 1px solid {c['glass_border']};
    border-radius: 16px;
    padding: 28px 24px;
    transition: all 0.25s ease;
    height: 100%;
}}
.landing-testimonial-card:hover {{
    border-color: {c['border_hover']};
    transform: translateY(-2px);
}}
.landing-testimonial-stars {{
    color: #FBBF24;
    font-size: 0.85rem;
    margin-bottom: 12px;
    letter-spacing: 2px;
}}
.landing-testimonial-quote {{
    font-size: 0.88rem;
    color: {c['text_muted']};
    line-height: 1.65;
    margin-bottom: 20px;
    font-style: italic;
}}
.landing-testimonial-author {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
.landing-testimonial-name {{
    font-size: 0.85rem;
    font-weight: 700;
    color: {c['text_primary']};
}}
.landing-testimonial-role {{
    font-size: 0.7rem;
    color: {c['text_dim']};
}}
.landing-cta-section {{
    position: relative;
    text-align: center;
    padding: 64px 24px 24px;
    overflow: hidden;
}}
.landing-cta-glow {{
    position: absolute;
    bottom: -80px; left: 50%;
    transform: translateX(-50%);
    width: 500px; height: 400px;
    background: radial-gradient(circle, {c['accent_glow']}, transparent 70%);
    pointer-events: none;
}}
.landing-cta-content {{
    position: relative;
    z-index: 1;
}}
.landing-cta-title {{
    font-size: 2rem;
    font-weight: 800;
    color: {c['text_primary']};
    letter-spacing: -0.03em;
    line-height: 1.25;
    margin-bottom: 12px;
}}
.landing-cta-desc {{
    font-size: 1rem;
    color: {c['text_dim']};
    max-width: 480px;
    margin: 0 auto 32px;
    line-height: 1.6;
}}
@media (max-width: 768px) {{
    .landing-hero-title {{
        font-size: 2.25rem !important;
    }}
    .landing-hero-stats-row {{
        gap: 20px;
    }}
    .landing-hero-stat-divider {{
        display: none;
    }}
    .landing-section-title {{
        font-size: 1.75rem;
    }}
}}
</style>"""
