"""
EventLens — Linear-inspired dark theme system.
Call inject_theme() once per page to apply the full design system.
"""
import base64
import os
from PIL import Image

import streamlit as st

# ── Color Palette (from PRD §18) ─────────────────────────────────────────
COLORS = {
    "bg_primary":   "#0F172A",
    "bg_secondary": "#1E293B",
    "bg_tertiary":  "#334155",
    "accent":       "#7C3AED",
    "accent_light": "#8B5CF6",
    "accent_glow":  "rgba(124,58,237,0.35)",
    "success":      "#10B981",
    "warning":      "#F59E0B",
    "error":        "#EF4444",
    "text_primary": "#F8FAFC",
    "text_muted":   "#94A3B8",
    "text_dim":     "#64748B",
    "border":       "rgba(148,163,184,0.12)",
    "border_hover": "rgba(148,163,184,0.25)",
    "glass_bg":     "rgba(30,41,59,0.65)",
    "glass_border": "rgba(148,163,184,0.10)",
}


def inject_theme():
    """Inject the complete CSS theme into the current Streamlit page."""
    st.markdown(_build_css(), unsafe_allow_html=True)


def _build_css() -> str:
    c = COLORS
    return f"""
<style>
/* ── Google Fonts ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root / Body ─────────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"] {{
    background-color: {c["bg_primary"]} !important;
    color: {c["text_primary"]} !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}

/* ── Scrollbar ───────────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {c["bg_tertiary"]}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {c["text_dim"]}; }}

/* ── Header bar hide ─────────────────────────────────────────────────── */
header[data-testid="stHeader"] {{
    background: {c["bg_primary"]} !important;
    border-bottom: 1px solid {c["border"]} !important;
}}

/* ── Sidebar ─────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
    background: {c["bg_secondary"]} !important;
    border-right: 1px solid {c["border"]} !important;
    padding-top: 1rem;
}}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] .stMarkdown label {{
    color: {c["text_muted"]} !important;
    font-size: 0.875rem;
}}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {{
    color: {c["text_primary"]} !important;
}}

/* Sidebar radio buttons → Linear nav style */
section[data-testid="stSidebar"] [data-testid="stRadio"] > div {{
    gap: 2px !important;
}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label {{
    background: transparent !important;
    border-radius: 6px !important;
    padding: 8px 12px !important;
    color: {c["text_muted"]} !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    transition: all 0.15s ease !important;
    border: none !important;
    cursor: pointer !important;
}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
    background: {c["bg_tertiary"]} !important;
    color: {c["text_primary"]} !important;
}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
section[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] {{
    background: {c["accent_glow"]} !important;
    color: {c["text_primary"]} !important;
}}
/* Hide the radio circle */
section[data-testid="stSidebar"] [data-testid="stRadio"] input {{
    display: none !important;
}}

/* Sidebar divider */
section[data-testid="stSidebar"] hr {{
    border-color: {c["border"]} !important;
    margin: 0.75rem 0 !important;
}}

/* Sidebar buttons */
section[data-testid="stSidebar"] button {{
    background: transparent !important;
    border: 1px solid {c["border"]} !important;
    color: {c["text_muted"]} !important;
    border-radius: 6px !important;
    font-size: 0.8rem !important;
    transition: all 0.15s ease !important;
}}
section[data-testid="stSidebar"] button:hover {{
    background: {c["bg_tertiary"]} !important;
    border-color: {c["border_hover"]} !important;
    color: {c["text_primary"]} !important;
}}

/* ── Main content area ───────────────────────────────────────────────── */
.main .block-container {{
    padding-top: 2rem !important;
    max-width: 1200px !important;
}}

/* ── Headings ────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {{
    color: {c["text_primary"]} !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em;
}}
h1 {{ font-size: 1.875rem !important; font-weight: 700 !important; }}
h2 {{ font-size: 1.375rem !important; }}
h3 {{ font-size: 1.125rem !important; }}

/* ── Markdown text ───────────────────────────────────────────────────── */
.stMarkdown p, .stMarkdown li, .stMarkdown span {{
    color: {c["text_muted"]} !important;
}}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: transparent !important;
    border-bottom: 1px solid {c["border"]} !important;
    gap: 0 !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {c["text_dim"]} !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    transition: all 0.15s ease !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    color: {c["text_primary"]} !important;
}}
.stTabs [aria-selected="true"] {{
    color: {c["text_primary"]} !important;
    border-bottom-color: {c["accent"]} !important;
    background: transparent !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{
    background-color: {c["accent"]} !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    padding-top: 1.5rem !important;
}}

/* ── Metric cards ────────────────────────────────────────────────────── */
[data-testid="stMetric"] {{
    background: {c["glass_bg"]} !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid {c["glass_border"]} !important;
    border-radius: 12px !important;
    padding: 20px 24px !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stMetric"]:hover {{
    border-color: {c["border_hover"]} !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.25);
}}
[data-testid="stMetric"] label {{
    color: {c["text_dim"]} !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}}
[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {c["text_primary"]} !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
}}
[data-testid="stMetric"] [data-testid="stMetricDelta"] {{
    font-size: 0.75rem !important;
}}

/* ── Buttons ─────────────────────────────────────────────────────────── */
.stButton > button {{
    background: linear-gradient(135deg, {c["accent"]}, {c["accent_light"]}) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
    letter-spacing: -0.01em;
}}
.stButton > button:hover {{
    opacity: 0.9 !important;
    box-shadow: 0 4px 16px {c["accent_glow"]} !important;
    transform: translateY(-1px);
}}
.stButton > button:active {{
    transform: translateY(0);
}}

/* ── Text Inputs ─────────────────────────────────────────────────────── */
.stTextInput input, .stTextArea textarea, .stSelectbox select,
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea {{
    background-color: {c["bg_primary"]} !important;
    color: {c["text_primary"]} !important;
    border: 1px solid {c["border"]} !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color 0.15s ease !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: {c["accent"]} !important;
    box-shadow: 0 0 0 2px {c["accent_glow"]} !important;
}}

/* Select boxes */
[data-baseweb="select"] > div {{
    background-color: {c["bg_primary"]} !important;
    border: 1px solid {c["border"]} !important;
    border-radius: 8px !important;
}}
[data-baseweb="select"] span {{
    color: {c["text_primary"]} !important;
}}
[data-baseweb="popover"] {{
    background-color: {c["bg_secondary"]} !important;
    border: 1px solid {c["border"]} !important;
}}
[data-baseweb="popover"] li {{
    color: {c["text_primary"]} !important;
}}
[data-baseweb="popover"] li:hover {{
    background-color: {c["bg_tertiary"]} !important;
}}

/* Date inputs */
.stDateInput > div > div {{
    background-color: {c["bg_primary"]} !important;
    border: 1px solid {c["border"]} !important;
    border-radius: 8px !important;
}}
.stDateInput input {{
    color: {c["text_primary"]} !important;
}}

/* ── Labels ──────────────────────────────────────────────────────────── */
.stTextInput label, .stTextArea label, .stSelectbox label,
.stRadio label, .stDateInput label, .stFileUploader label,
.stCheckbox label {{
    color: {c["text_muted"]} !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}}

/* ── Expander ────────────────────────────────────────────────────────── */
details[data-testid="stExpander"] {{
    background: {c["glass_bg"]} !important;
    border: 1px solid {c["glass_border"]} !important;
    border-radius: 12px !important;
    backdrop-filter: blur(12px) !important;
}}
details[data-testid="stExpander"] summary {{
    color: {c["text_primary"]} !important;
    font-weight: 500 !important;
}}

/* ── Alerts ──────────────────────────────────────────────────────────── */
.stAlert {{
    border-radius: 8px !important;
    font-size: 0.875rem !important;
}}
[data-testid="stAlert"] {{
    background: {c["glass_bg"]} !important;
    border: 1px solid {c["glass_border"]} !important;
    border-radius: 10px !important;
}}

/* ── File Uploader ───────────────────────────────────────────────────── */
[data-testid="stFileUploader"] > div {{
    background: {c["bg_primary"]} !important;
    border: 2px dashed {c["border"]} !important;
    border-radius: 12px !important;
    transition: border-color 0.2s ease !important;
}}
[data-testid="stFileUploader"] > div:hover {{
    border-color: {c["accent"]} !important;
}}

/* ── Spinner ─────────────────────────────────────────────────────────── */
.stSpinner > div {{
    border-top-color: {c["accent"]} !important;
}}

/* ── Dividers ────────────────────────────────────────────────────────── */
hr {{
    border-color: {c["border"]} !important;
}}

/* ── Toast / Success / Error ─────────────────────────────────────────── */
.stSuccess {{
    background: rgba(16,185,129,0.1) !important;
    border-left: 3px solid {c["success"]} !important;
    color: {c["success"]} !important;
}}

/* ── Code blocks ─────────────────────────────────────────────────────── */
code {{
    background-color: {c["bg_tertiary"]} !important;
    color: {c["accent_light"]} !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 0.8rem !important;
}}
pre {{
    background-color: {c["bg_secondary"]} !important;
    border: 1px solid {c["border"]} !important;
    border-radius: 8px !important;
}}

/* ── Camera input ────────────────────────────────────────────────────── */
[data-testid="stCameraInput"] > div {{
    border: 2px solid {c["border"]} !important;
    border-radius: 12px !important;
    overflow: hidden;
}}

/* ── Image styling ───────────────────────────────────────────────────── */
[data-testid="stImage"] {{
    border-radius: 8px !important;
    overflow: hidden;
}}

/* ═══════════════════════════════════════════════════════════════════════
   CUSTOM COMPONENT CLASSES (injected via st.markdown)
   ═══════════════════════════════════════════════════════════════════════ */

/* Glass Card */
.glass-card {{
    background: {c["glass_bg"]};
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid {c["glass_border"]};
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 16px;
    transition: all 0.2s ease;
}}
.glass-card:hover {{
    border-color: {c["border_hover"]};
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}}

/* Metric Card (used in HTML injection) */
.metric-card {{
    background: {c["glass_bg"]};
    backdrop-filter: blur(12px);
    border: 1px solid {c["glass_border"]};
    border-radius: 14px;
    padding: 24px 28px;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}}
.metric-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, {c["accent"]}, {c["accent_light"]});
    border-radius: 14px 14px 0 0;
}}
.metric-card:hover {{
    border-color: {c["border_hover"]};
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.25);
}}
.metric-card .metric-icon {{
    font-size: 1.5rem;
    margin-bottom: 12px;
}}
.metric-card .metric-value {{
    font-size: 2rem;
    font-weight: 800;
    color: {c["text_primary"]};
    line-height: 1;
    margin-bottom: 6px;
    letter-spacing: -0.03em;
}}
.metric-card .metric-label {{
    font-size: 0.75rem;
    color: {c["text_dim"]};
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
}}

/* Event Card */
.event-card {{
    background: {c["glass_bg"]};
    backdrop-filter: blur(12px);
    border: 1px solid {c["glass_border"]};
    border-radius: 14px;
    padding: 24px;
    cursor: pointer;
    transition: all 0.2s ease;
}}
.event-card:hover {{
    border-color: {c["accent"]};
    box-shadow: 0 4px 24px {c["accent_glow"]};
    transform: translateY(-2px);
}}
.event-card .event-name {{
    font-size: 1.1rem;
    font-weight: 600;
    color: {c["text_primary"]};
    margin-bottom: 8px;
}}
.event-card .event-meta {{
    font-size: 0.8rem;
    color: {c["text_dim"]};
    margin-bottom: 4px;
}}
.event-card .event-stats {{
    display: flex;
    gap: 16px;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid {c["border"]};
}}
.event-card .stat-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
}}
.event-card .stat-value {{
    font-size: 1.125rem;
    font-weight: 700;
    color: {c["text_primary"]};
}}
.event-card .stat-label {{
    font-size: 0.65rem;
    color: {c["text_dim"]};
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

/* Status Badge */
.status-badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}
.status-active {{
    background: rgba(16,185,129,0.15);
    color: {c["success"]};
    border: 1px solid rgba(16,185,129,0.3);
}}
.status-processing {{
    background: rgba(245,158,11,0.15);
    color: {c["warning"]};
    border: 1px solid rgba(245,158,11,0.3);
}}
.status-completed {{
    background: rgba(124,58,237,0.15);
    color: {c["accent_light"]};
    border: 1px solid rgba(124,58,237,0.3);
}}
.status-error {{
    background: rgba(239,68,68,0.15);
    color: {c["error"]};
    border: 1px solid rgba(239,68,68,0.3);
}}

/* Pipeline Stage Tracker */
.pipeline-tracker {{
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 16px 0;
    flex-wrap: wrap;
}}
.pipeline-stage {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 500;
    background: {c["bg_tertiary"]};
    color: {c["text_dim"]};
    transition: all 0.3s ease;
}}
.pipeline-stage.active {{
    background: {c["accent_glow"]};
    color: {c["text_primary"]};
    animation: pulse 1.5s infinite;
}}
.pipeline-stage.completed {{
    background: rgba(16,185,129,0.15);
    color: {c["success"]};
}}
.pipeline-connector {{
    width: 20px;
    height: 2px;
    background: {c["bg_tertiary"]};
}}
.pipeline-connector.completed {{
    background: {c["success"]};
}}

/* Hero Section (Auth / Guest) */
.hero-section {{
    text-align: center;
    padding: 48px 24px;
}}
.hero-title {{
    font-size: 2.75rem;
    font-weight: 800;
    background: linear-gradient(135deg, {c["text_primary"]}, {c["accent_light"]});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    letter-spacing: -0.03em;
    margin-bottom: 16px;
}}
.hero-subtitle {{
    font-size: 1.125rem;
    color: {c["text_dim"]};
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.6;
}}

/* Auth Card */
.auth-card {{
    background: {c["glass_bg"]};
    backdrop-filter: blur(16px);
    border: 1px solid {c["glass_border"]};
    border-radius: 16px;
    padding: 36px 32px;
    max-width: 420px;
    margin: 0 auto;
}}

/* Guest Result Gallery */
.photo-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 16px;
}}
.photo-item {{
    position: relative;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid {c["glass_border"]};
    transition: all 0.2s ease;
}}
.photo-item:hover {{
    border-color: {c["accent"]};
    transform: scale(1.02);
}}
.photo-item img {{
    width: 100%;
    display: block;
}}

/* Activity Feed */
.activity-item {{
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid {c["border"]};
}}
.activity-icon {{
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    flex-shrink: 0;
}}
.activity-text {{
    font-size: 0.85rem;
    color: {c["text_muted"]};
    line-height: 1.5;
}}
.activity-time {{
    font-size: 0.7rem;
    color: {c["text_dim"]};
    margin-top: 2px;
}}

/* ── Animations ──────────────────────────────────────────────────────── */
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.7; }}
}}
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes shimmer {{
    0%   {{ background-position: -200% 0; }}
    100% {{ background-position: 200% 0; }}
}}
@keyframes slideUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.fade-in {{
    animation: fadeIn 0.4s ease forwards;
}}
.slide-up {{
    animation: slideUp 0.5s ease forwards;
}}

/* Skeleton loader */
.skeleton {{
    background: linear-gradient(90deg, {c["bg_tertiary"]} 25%, {c["bg_secondary"]} 50%, {c["bg_tertiary"]} 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 8px;
}}

/* ── Responsive ──────────────────────────────────────────────────────── */
@media (max-width: 768px) {{
    .hero-title {{ font-size: 2rem; }}
    .photo-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .metric-card .metric-value {{ font-size: 1.5rem; }}
    .pipeline-tracker {{ flex-direction: column; align-items: flex-start; }}
    .pipeline-connector {{ width: 2px; height: 12px; margin-left: 20px; }}
}}
</style>
"""


# ── Helper functions for injecting HTML components ────────────────────────

def metric_card(icon: str, value: str, label: str) -> str:
    """Return HTML for a single glassmorphism metric card."""
    return f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


def status_badge(text: str, variant: str = "active") -> str:
    """Return HTML for a status badge. Variants: active, processing, completed, error."""
    return f'<span class="status-badge status-{variant}">{text}</span>'


def event_card_html(name: str, date: str, location: str, event_type: str,
                    photo_count: int = 0, face_count: int = 0, status: str = "active") -> str:
    """Return HTML for an event card."""
    badge = status_badge(status, status)
    return f"""
    <div class="event-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div class="event-name">{name}</div>
            {badge}
        </div>
        <div class="event-meta">📅 {date} &nbsp;·&nbsp; 📍 {location}</div>
        <div class="event-meta">🏷️ {event_type}</div>
        <div class="event-stats">
            <div class="stat-item">
                <span class="stat-value">{photo_count}</span>
                <span class="stat-label">Photos</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">{face_count}</span>
                <span class="stat-label">Faces</span>
            </div>
        </div>
    </div>
    """


def pipeline_stage_html(stages: list, current_index: int = -1) -> str:
    """Return HTML for a pipeline progress tracker.

    stages: list of (emoji, label) tuples
    current_index: index of the currently active stage (-1 = none, len = all complete)
    """
    html_parts = []
    for i, (emoji, label) in enumerate(stages):
        if i < current_index:
            cls = "pipeline-stage completed"
        elif i == current_index:
            cls = "pipeline-stage active"
        else:
            cls = "pipeline-stage"
        html_parts.append(f'<div class="{cls}">{emoji} {label}</div>')
        if i < len(stages) - 1:
            conn_cls = "pipeline-connector completed" if i < current_index else "pipeline-connector"
            html_parts.append(f'<div class="{conn_cls}"></div>')
    return f'<div class="pipeline-tracker">{"".join(html_parts)}</div>'


def get_logo_image():
    """Load the logo PIL Image from e:\\Projects\\eventSNAP1\\image.png."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    paths_to_try = [
        os.path.abspath(os.path.join(current_dir, "..", "..", "image.png")),
        os.path.abspath(os.path.join(current_dir, "..", "image.png")),
        os.path.abspath(os.path.join(current_dir, "image.png")),
        "image.png"
    ]
    for p in paths_to_try:
        if os.path.exists(p):
            try:
                return Image.open(p)
            except Exception:
                pass
    return None


def get_logo_base64() -> str:
    """Return the base64 encoded string of the logo image."""
    logo = get_logo_image()
    if logo:
        import io
        buffered = io.BytesIO()
        logo.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    return ""


def get_logo_html(height: int = 24, width: int = 24, label: str = "EventLens") -> str:
    """Return HTML snippet containing logo image and label."""
    b64 = get_logo_base64()
    if b64:
        return f"""
        <div style="display: flex; align-items: center; gap: 10px; padding: 4px 0 12px 0;">
            <img src="data:image/png;base64,{b64}" style="height: {height}px; width: {width}px; object-fit: contain; border-radius: 4px;" />
            <span style="font-size: 1.35rem; font-weight: 700; color: #F8FAFC; letter-spacing: -0.03em;">
                {label}
            </span>
        </div>
        """
    else:
        # Fallback to emoji if image is not found
        return f"""
        <div style="display: flex; align-items: center; gap: 10px; padding: 4px 0 12px 0;">
            <span style="font-size: 1.35rem;">📸</span>
            <span style="font-size: 1.35rem; font-weight: 700; color: #F8FAFC; letter-spacing: -0.03em;">
                {label}
            </span>
        </div>
        """

