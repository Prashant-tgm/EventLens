"""
EventLens AI — Premium Footer Component.
Rich footer with multi-column links, branding, social icons, and legal links.
Uses only div-based HTML for full Streamlit compatibility.
"""
import streamlit as st
from utils.theme import get_logo_base64, COLORS


def show_footer():
    """Render the premium site-wide footer."""

    logo_b64 = get_logo_base64()
    c = COLORS

    logo_html = ""
    if logo_b64:
        logo_html = (
            f'<img src="data:image/png;base64,{logo_b64}" '
            f'style="height:28px;width:28px;object-fit:contain;border-radius:6px;" '
            f'alt="EventLens" />'
        )
    else:
        logo_html = '<span style="font-size:1.4rem;">📸</span>'

    # ── Inject footer CSS ────────────────────────────────────────────────
    st.markdown(f"""<style>
.el-footer {{
    margin-top: 64px;
    border-top: 1px solid {c['border']};
    background: {c['bg_secondary']};
    padding: 56px 32px 0 32px;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}}
.el-footer-inner {{
    max-width: 1100px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 40px;
}}
.el-footer-brand {{
    display: flex;
    flex-direction: column;
    gap: 16px;
}}
.el-footer-logo {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
.el-footer-logo-text {{
    font-size: 1.2rem;
    font-weight: 700;
    color: {c['text_primary']};
    letter-spacing: -0.02em;
}}
.el-footer-tagline {{
    font-size: 0.85rem;
    color: {c['text_dim']};
    line-height: 1.65;
    max-width: 280px;
}}
.el-footer-socials {{
    display: flex;
    gap: 12px;
    margin-top: 8px;
}}
.el-footer-social {{
    width: 36px; height: 36px;
    border-radius: 10px;
    background: {c['bg_tertiary']};
    border: 1px solid {c['border']};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    color: {c['text_muted']};
    transition: all 0.2s ease;
    cursor: pointer;
    font-weight: 700;
}}
.el-footer-social:hover {{
    background: {c['accent']};
    color: #fff;
    border-color: {c['accent']};
    transform: translateY(-2px);
    box-shadow: 0 4px 16px {c['accent_glow']};
}}
.el-footer-col-title {{
    font-size: 0.7rem;
    color: {c['text_dim']};
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 700;
    margin-bottom: 20px;
}}
.el-footer-link-list {{
    display: flex;
    flex-direction: column;
    gap: 12px;
}}
.el-footer-link {{
    font-size: 0.85rem;
    color: {c['text_muted']};
    transition: color 0.15s ease;
    cursor: pointer;
}}
.el-footer-link:hover {{
    color: {c['text_primary']};
}}
.el-footer-bottom {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 24px 0;
    margin-top: 48px;
    border-top: 1px solid {c['border']};
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}}
.el-footer-copy {{
    font-size: 0.75rem;
    color: {c['text_dim']};
}}
.el-footer-legal {{
    display: flex;
    gap: 20px;
}}
.el-footer-legal-link {{
    font-size: 0.75rem;
    color: {c['text_dim']};
    cursor: pointer;
    transition: color 0.15s ease;
}}
.el-footer-legal-link:hover {{
    color: {c['text_muted']};
}}
.el-footer-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: {c['bg_tertiary']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 0.65rem;
    color: {c['text_dim']};
    font-weight: 500;
}}
.el-footer-badge-dot {{
    width: 5px; height: 5px;
    border-radius: 50%;
    background: {c['success']};
    box-shadow: 0 0 6px {c['success']};
    display: inline-block;
}}
@media (max-width: 768px) {{
    .el-footer-inner {{
        grid-template-columns: 1fr;
        gap: 32px;
    }}
    .el-footer-bottom {{
        flex-direction: column;
        text-align: center;
    }}
    .el-footer-legal {{
        justify-content: center;
    }}
}}
</style>""", unsafe_allow_html=True)

    # ── Render footer HTML (div-only, no ul/li/footer/a tags) ─────────────
    st.markdown(f"""
<div class="el-footer">
    <div class="el-footer-inner">
        <div class="el-footer-brand">
            <div class="el-footer-logo">
                {logo_html}
                <span class="el-footer-logo-text">EventLens</span>
            </div>
            <div class="el-footer-tagline">
                AI-powered event photo retrieval. Upload once, let facial
                recognition handle the rest. Every guest, every photo, instantly.
            </div>
            <div class="el-footer-socials">
                <div class="el-footer-social" title="Twitter">X</div>
                <div class="el-footer-social" title="LinkedIn">in</div>
                <div class="el-footer-social" title="GitHub">GH</div>
                <div class="el-footer-social" title="Instagram">IG</div>
            </div>
        </div>
        <div>
            <div class="el-footer-col-title">Product</div>
            <div class="el-footer-link-list">
                <div class="el-footer-link">Features</div>
                <div class="el-footer-link">Pricing</div>
                <div class="el-footer-link">Integrations</div>
                <div class="el-footer-link">API</div>
                <div class="el-footer-link">Changelog</div>
            </div>
        </div>
        <div>
            <div class="el-footer-col-title">Resources</div>
            <div class="el-footer-link-list">
                <div class="el-footer-link">Documentation</div>
                <div class="el-footer-link">Blog</div>
                <div class="el-footer-link">Case Studies</div>
                <div class="el-footer-link">Support</div>
                <div class="el-footer-link">Status</div>
            </div>
        </div>
        <div>
            <div class="el-footer-col-title">Company</div>
            <div class="el-footer-link-list">
                <div class="el-footer-link">About</div>
                <div class="el-footer-link">Careers</div>
                <div class="el-footer-link">Contact</div>
                <div class="el-footer-link">Press</div>
                <div class="el-footer-link">Partners</div>
            </div>
        </div>
    </div>
    <div class="el-footer-bottom">
        <span class="el-footer-copy">
            &copy; 2026 EventLens AI. All rights reserved.
        </span>
        <div class="el-footer-badge">
            <span class="el-footer-badge-dot"></span>
            All systems operational
        </div>
        <div class="el-footer-legal">
            <span class="el-footer-legal-link">Privacy Policy</span>
            <span class="el-footer-legal-link">Terms of Service</span>
            <span class="el-footer-legal-link">Cookie Settings</span>
        </div>
    </div>
</div>
    """, unsafe_allow_html=True)
